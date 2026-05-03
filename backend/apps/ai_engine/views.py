import json
from collections import Counter
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import TestFile, CodeFile, ChangeEvent
from .watsonx_client import generate_tests, update_tests, _USE_MOCK


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_tests_view(request):
    code_snippet = request.data.get('code', '')
    language = request.data.get('language', 'python')

    if not code_snippet:
        return Response(
            {'error': 'No code provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tests = generate_tests(code_snippet, language)
        return Response({
            'status': 'success',
            'tests': tests,
            'language': language
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def update_tests_view(request):
    original_code = request.data.get('original_code', '')
    updated_code = request.data.get('updated_code', '')
    existing_tests = request.data.get('existing_tests', '')

    if not all([original_code, updated_code, existing_tests]):
        return Response(
            {'error': 'original_code, updated_code and existing_tests are all required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        updated = update_tests(original_code, updated_code, existing_tests)
        return Response({
            'status': 'success',
            'updated_tests': updated
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_test_files(request):
    repo_id = request.query_params.get('repo')
    if not repo_id:
        return Response({'error': 'repo parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    test_files = TestFile.objects.filter(
        code_file__repo_id=repo_id
    ).select_related('code_file')

    data = [
        {
            'id': tf.id,
            'is_passing': tf.is_passing,
            'generated_by_ai': tf.generated_by_ai,
            'last_updated': tf.last_updated.isoformat(),
            'created_at': tf.created_at.isoformat(),
            'code_file': {
                'id': tf.code_file.id,
                'file_path': tf.code_file.file_path,
                'language': tf.code_file.language,
                'repo': {'id': tf.code_file.repo_id},
            },
        }
        for tf in test_files
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_test_file(request, test_id):
    try:
        tf = TestFile.objects.select_related(
            'code_file', 'code_file__repo'
        ).prefetch_related('code_file__change_events').get(id=test_id)
    except TestFile.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    change_events = [
        {
            'id': ce.id,
            'commit_hash': ce.commit_hash,
            'commit_message': ce.commit_message,
            'status': ce.status,
            'detected_at': ce.detected_at.isoformat(),
        }
        for ce in tf.code_file.change_events.order_by('-detected_at')
    ]

    return Response({
        'id': tf.id,
        'test_content': tf.test_content,
        'is_passing': tf.is_passing,
        'generated_by_ai': tf.generated_by_ai,
        'last_updated': tf.last_updated.isoformat(),
        'created_at': tf.created_at.isoformat(),
        'code_file': {
            'id': tf.code_file.id,
            'file_path': tf.code_file.file_path,
            'file_content': tf.code_file.file_content,
            'language': tf.code_file.language,
            'repo': {'id': tf.code_file.repo_id},
            'change_events': change_events,
        },
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def repo_overview(request, repo_id):
    from apps.github_integration.models import GitHubRepo

    cache_key = f'repo_overview_{repo_id}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)

    # Gather full context from DB
    code_files = CodeFile.objects.filter(repo=repo)
    test_files = TestFile.objects.filter(code_file__repo=repo).select_related('code_file')
    recent_changes = list(
        ChangeEvent.objects.filter(code_file__repo=repo)
        .select_related('code_file')
        .order_by('-detected_at')[:5]
    )

    total_files = code_files.count()
    test_count = test_files.count()
    passing = test_files.filter(is_passing=True).count()
    coverage_pct = round((test_count / total_files * 100) if total_files > 0 else 0)
    pass_rate_pct = round((passing / test_count * 100) if test_count > 0 else 0, 1)
    untested_count = max(0, total_files - test_count)

    lang_counts = Counter(cf.language for cf in code_files if cf.language)
    lang_breakdown = ', '.join(
        f'{lang}: {count} files' for lang, count in lang_counts.most_common(5)
    )

    changes_text = '\n'.join(
        f"- {(ce.commit_hash[:8] if ce.commit_hash else 'unknown')}: {ce.code_file.file_path}"
        for ce in recent_changes
    ) or 'No recent changes recorded'

    test_sample = '\n'.join(
        f"- {tf.code_file.file_path}: {len(tf.test_content or '')} chars of tests"
        for tf in test_files[:5]
    ) or 'No tests generated yet'

    failed_tests = test_files.filter(is_passing=False)
    failed_paths = [tf.code_file.file_path for tf in failed_tests[:5]]
    failed_str = ', '.join(failed_paths) or 'none'

    if _USE_MOCK:
        # Generate a data-driven mock overview without calling WatsonX
        if recent_changes:
            risk_text = (
                f'Recent commits touched: '
                f'{", ".join(ce.code_file.file_path for ce in recent_changes)}. '
                + (
                    f'Failing tests detected in: {failed_str}.'
                    if failed_tests.exists()
                    else 'All tests for changed files are currently passing.'
                )
            )
        else:
            risk_text = (
                'No recent ChangeEvents recorded. '
                'Webhook may not be active — push a commit or verify the GitHub webhook secret '
                f'configured for {repo.repo_name}.'
            )

        recommendations = []
        if untested_count > 0:
            recommendations.append(
                f'Generate tests for the {untested_count} {repo.repo_name} files still missing coverage.'
            )
        else:
            recommendations.append(
                f'All {total_files} analyzed files have tests — run them in CI to verify they actually pass.'
            )

        if lang_counts:
            top_lang, top_count = lang_counts.most_common(1)[0]
            recommendations.append(
                f'Most of {repo.repo_name} is {top_lang} ({top_count} files) — '
                f'prioritize a {top_lang} test runner in CI.'
            )
        else:
            recommendations.append(
                f'Re-run the initial scan for {repo.repo_name} — language detection returned no results.'
            )

        recommendations.append(
            f'Configure the GitHub webhook on {repo.repo_name} so Zero Touch regenerates tests on every push.'
        )

        result = {
            'summary': (
                f'{repo.repo_name} is a {lang_breakdown or "multi-language"} project '
                f'with {total_files} analyzed source files. '
                f'Zero Touch has generated {test_count} test files providing '
                f'{coverage_pct}% file-level coverage.'
            ),
            'coverage_assessment': (
                f'{coverage_pct}% coverage across {total_files} files '
                f'({test_count} test files generated, {passing} passing — {pass_rate_pct}% pass rate). '
                + (
                    'Coverage is strong.'
                    if coverage_pct >= 80
                    else f'{untested_count} files still need tests'
                    + (f' (failing: {failed_str})' if failed_tests.exists() else '')
                    + '.'
                )
            ),
            'risk_areas': risk_text,
            'recommendations': recommendations,
        }
    else:
        prompt = (
            f"You are a senior software engineer reviewing a specific codebase. "
            f"Here is the REAL data for this repo:\n\n"
            f"Repository: {repo.repo_name}\n"
            f"Languages detected: {lang_breakdown or 'unknown'}\n"
            f"Total source files analyzed: {total_files}\n"
            f"Test files generated: {test_count}\n"
            f"Estimated file-level coverage: {coverage_pct}%\n"
            f"Pass rate: {pass_rate_pct}% ({passing}/{test_count})\n\n"
            f"Recent git changes:\n{changes_text}\n\n"
            f"Test files generated (sample):\n{test_sample}\n\n"
            f"Failing tests: {failed_str}\n\n"
            f"Based on this SPECIFIC data, provide a technical analysis. "
            f"Do not give generic advice. Reference the actual file names, "
            f"languages, and numbers above. Mention {repo.repo_name} by name.\n\n"
            f"Return ONLY valid JSON, no markdown, no explanation:\n"
            f'{{"summary": "2 sentences describing what {repo.repo_name} does based on its '
            f'file structure and languages", "coverage_assessment": "specific assessment '
            f'using the {coverage_pct}% coverage number and actual file counts", '
            f'"risk_areas": "specific risks based on the actual recent changes listed above", '
            f'"recommendations": ["specific action 1 referencing actual files", '
            f'"specific action 2 referencing actual languages", '
            f'"specific action 3 referencing actual coverage gap"]}}'
        )
        try:
            from .watsonx_client import _get_model
            model = _get_model()
            raw = model.generate_text(prompt=prompt)
            try:
                result = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                result = {
                    'summary': str(raw),
                    'coverage_assessment': '',
                    'risk_areas': '',
                    'recommendations': [],
                }
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    cache.set(cache_key, result, 300)
    return Response(result)

# Made with Bob
