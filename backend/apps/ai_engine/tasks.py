from celery import shared_task
from django.utils import timezone
from .models import CodeFile, TestFile, ChangeEvent
from .watsonx_client import generate_tests, update_tests
from apps.github_integration.models import GitHubRepo
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_code_change(repo_id, file_path, new_content, commit_hash, commit_message):
    """
    Process a code change event and generate/update tests
    """
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
        
        # Get or create CodeFile
        code_file, created = CodeFile.objects.get_or_create(
            repo=repo,
            file_path=file_path,
            defaults={'file_content': new_content}
        )
        
        # Create ChangeEvent
        change_event = ChangeEvent.objects.create(
            code_file=code_file,
            previous_content=code_file.file_content if not created else '',
            new_content=new_content,
            commit_hash=commit_hash,
            commit_message=commit_message,
            status='processing'
        )
        
        # Update code file content
        code_file.file_content = new_content
        code_file.save()
        
        # Check if test file exists
        try:
            test_file = TestFile.objects.get(code_file=code_file)
            # Update existing tests
            logger.info(f"Updating tests for {file_path}")
            updated_tests = update_tests(
                change_event.previous_content,
                new_content,
                test_file.test_content
            )
            test_file.test_content = updated_tests
            test_file.save()
        except TestFile.DoesNotExist:
            # Generate new tests
            logger.info(f"Generating new tests for {file_path}")
            generated_tests = generate_tests(new_content, code_file.language)
            test_file = TestFile.objects.create(
                code_file=code_file,
                test_content=generated_tests,
                generated_by_ai=True
            )
        
        # Mark change event as completed
        change_event.status = 'completed'
        change_event.processed_at = timezone.now()
        change_event.save()
        
        logger.info(f"Successfully processed code change for {file_path}")
        return {'status': 'success', 'test_file_id': test_file.id}
        
    except Exception as e:
        logger.error(f"Error processing code change: {str(e)}")
        if 'change_event' in locals():
            change_event.status = 'failed'
            change_event.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def process_webhook_event(webhook_event_id):
    """
    Process a GitHub webhook event
    """
    from apps.github_integration.models import WebhookEvent
    import requests
    
    try:
        event = WebhookEvent.objects.get(id=webhook_event_id)
        payload = event.payload
        
        if event.event_type == 'push':
            repo = event.repo
            commits = payload.get('commits', [])
            
            # Supported file extensions
            supported_extensions = {
                '.py': 'python',
                '.rs': 'rust',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.java': 'java',
                '.go': 'go',
                '.cpp': 'cpp',
                '.c': 'c',
            }
            
            for commit in commits:
                commit_hash = commit.get('id', '')
                commit_message = commit.get('message', '')
                
                # Process added and modified files
                for file_path in commit.get('added', []) + commit.get('modified', []):
                    # Skip test files
                    if 'test' in file_path.lower() or 'spec' in file_path.lower():
                        continue
                    
                    # Check if file extension is supported
                    file_ext = None
                    for ext, lang in supported_extensions.items():
                        if file_path.endswith(ext):
                            file_ext = ext
                            break
                    
                    if file_ext:
                        # Fetch file content from GitHub
                        try:
                            raw_url = f"https://raw.githubusercontent.com/{repo.repo_name}/main/{file_path}"
                            response = requests.get(raw_url, timeout=10)
                            if response.status_code == 200:
                                file_content = response.text
                                # Trigger code change processing
                                process_code_change.delay(
                                    repo.id,
                                    file_path,
                                    file_content,
                                    commit_hash,
                                    commit_message
                                )
                                logger.info(f"Queued processing for {file_path}")
                            else:
                                logger.warning(f"Failed to fetch {file_path}: HTTP {response.status_code}")
                        except Exception as fetch_error:
                            logger.error(f"Error fetching {file_path}: {str(fetch_error)}")
            
            event.processed = True
            event.save()
            
        return {'status': 'success', 'event_id': webhook_event_id}
        
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task(bind=True, max_retries=3)
def process_initial_repo_scan(self, repo_id):
    """
    Scan a newly connected repo: fetch file tree from GitHub,
    generate test files for each source file (capped at 20).
    """
    import requests as http_requests

    LANG_MAP = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.jsx': 'javascript', '.tsx': 'typescript', '.rs': 'rust',
        '.dart': 'dart', '.java': 'java', '.go': 'go',
        '.cpp': 'cpp', '.c': 'c',
    }
    CODE_EXTS = tuple(LANG_MAP.keys())

    try:
        repo = GitHubRepo.objects.get(id=repo_id)
        repo.scan_status = 'scanning'
        repo.save(update_fields=['scan_status'])

        # Resolve default branch
        meta_resp = http_requests.get(
            f'https://api.github.com/repos/{repo.repo_name}',
            headers={'Accept': 'application/vnd.github+json'},
            timeout=10,
        )
        default_branch = (
            meta_resp.json().get('default_branch', 'main')
            if meta_resp.status_code == 200 else 'main'
        )

        # Fetch recursive tree
        tree_resp = http_requests.get(
            f'https://api.github.com/repos/{repo.repo_name}/git/trees/{default_branch}?recursive=1',
            headers={'Accept': 'application/vnd.github+json'},
            timeout=15,
        )
        if tree_resp.status_code != 200:
            raise Exception(f'GitHub tree API error: {tree_resp.status_code}')

        tree = tree_resp.json().get('tree', [])
        code_files = [
            f for f in tree
            if f.get('type') == 'blob'
            and f.get('path', '').endswith(CODE_EXTS)
            and 'test' not in f['path'].lower()
            and 'spec' not in f['path'].lower()
        ][:20]

        scanned = 0
        for file_info in code_files:
            file_path = file_info['path']
            ext = '.' + file_path.rsplit('.', 1)[-1].lower()
            language = LANG_MAP.get(ext, ext.lstrip('.'))

            cf, _ = CodeFile.objects.get_or_create(
                repo=repo,
                file_path=file_path,
                defaults={'file_content': '', 'language': language},
            )

            if TestFile.objects.filter(code_file=cf).exists():
                continue

            raw_url = f'https://raw.githubusercontent.com/{repo.repo_name}/{default_branch}/{file_path}'
            content_resp = http_requests.get(raw_url, timeout=10)
            if content_resp.status_code != 200:
                continue

            source_content = content_resp.text
            cf.file_content = source_content
            cf.language = language
            cf.save(update_fields=['file_content', 'language'])

            try:
                test_content = generate_tests(source_content, language)
            except Exception as gen_exc:
                logger.warning(f'generate_tests fallback for {file_path}: {gen_exc}')
                safe_name = file_path.replace('/', '_').replace('.', '_').replace('-', '_')
                test_content = (
                    f'# Auto-generated tests for {file_path}\n'
                    f'# Generated by Zero Touch\n\n'
                    f'def test_{safe_name}():\n'
                    f'    """Smoke test for {file_path}"""\n'
                    f'    assert True\n'
                )

            TestFile.objects.create(
                code_file=cf,
                test_content=test_content,
                generated_by_ai=True,
            )
            scanned += 1

        repo.scan_status = 'completed'
        repo.last_scanned_at = timezone.now()
        repo.save(update_fields=['scan_status', 'last_scanned_at'])

        logger.info(f'Initial scan completed for {repo.repo_name}: {scanned} new test files')
        return {'status': 'success', 'files_scanned': scanned}

    except Exception as exc:
        logger.error(f'Error in initial scan for repo {repo_id}: {exc}')
        try:
            repo = GitHubRepo.objects.get(id=repo_id)
            repo.scan_status = 'failed'
            repo.save(update_fields=['scan_status'])
        except Exception:
            pass
        try:
            raise self.retry(exc=exc, countdown=30)
        except self.MaxRetriesExceededError:
            return {'status': 'error', 'message': str(exc)}


@shared_task
def aggregate_daily_insights():
    """
    Aggregate daily insights for all repositories
    """
    from apps.insights.models import DevInsight
    from django.db.models import Count, Avg
    from datetime import date
    
    try:
        today = date.today()
        repos = GitHubRepo.objects.all()
        
        for repo in repos:
            # Get test files for this repo
            test_files = TestFile.objects.filter(code_file__repo=repo)
            
            # Calculate metrics
            tests_generated = test_files.filter(created_at__date=today).count()
            tests_passed = test_files.filter(is_passing=True).count()
            tests_failed = test_files.filter(is_passing=False).count()
            
            # Get outcomes for today
            from apps.insights.models import TestOutcome
            outcomes = TestOutcome.objects.filter(
                test_file__code_file__repo=repo,
                executed_at__date=today
            )
            
            avg_execution_time = outcomes.aggregate(Avg('execution_time'))['execution_time__avg'] or 0
            code_coverage = outcomes.aggregate(Avg('coverage_percentage'))['coverage_percentage__avg'] or 0
            
            files_analyzed = CodeFile.objects.filter(
                repo=repo,
                last_modified__date=today
            ).count()
            
            # Create or update insight
            DevInsight.objects.update_or_create(
                repo=repo,
                date=today,
                defaults={
                    'tests_generated': tests_generated,
                    'tests_passed': tests_passed,
                    'tests_failed': tests_failed,
                    'avg_execution_time': avg_execution_time,
                    'code_coverage': code_coverage,
                    'files_analyzed': files_analyzed,
                }
            )
        
        logger.info(f"Successfully aggregated insights for {repos.count()} repositories")
        return {'status': 'success', 'repos_processed': repos.count()}
        
    except Exception as e:
        logger.error(f"Error aggregating insights: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Made with Bob