import hashlib
import hmac
import json
import secrets
import requests as http_requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import GitHubRepo, WebhookEvent


@csrf_exempt
@require_POST
def github_webhook(request):
    secret = settings.GITHUB_WEBHOOK_SECRET.encode('utf-8')
    signature = request.headers.get('X-Hub-Signature-256', '')
    body = request.body

    expected = 'sha256=' + hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return JsonResponse({'error': 'Invalid signature'}, status=403)

    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    payload = json.loads(body)

    if event_type == 'push':
        repo_url = payload.get('repository', {}).get('html_url', '')
        repo_name = payload.get('repository', {}).get('full_name', '')
        repo, _ = GitHubRepo.objects.get_or_create(
            repo_url=repo_url,
            defaults={'repo_name': repo_name, 'github_token': ''}
        )
        webhook_event = WebhookEvent.objects.create(
            repo=repo,
            event_type=event_type,
            payload=payload
        )
        
        # Trigger async processing
        from apps.ai_engine.tasks import process_webhook_event
        process_webhook_event.delay(webhook_event.id)

    return JsonResponse({'status': 'received', 'event': event_type})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_repos(request):
    """List all connected GitHub repositories"""
    from apps.ai_engine.models import CodeFile, TestFile
    repos = GitHubRepo.objects.filter(is_active=True)
    data = []
    for repo in repos:
        file_count = CodeFile.objects.filter(repo=repo).count()
        test_count = TestFile.objects.filter(code_file__repo=repo).count()
        passing_count = TestFile.objects.filter(code_file__repo=repo, is_passing=True).count()
        data.append({
            'id': repo.id,
            'repo_name': repo.repo_name,
            'repo_url': repo.repo_url,
            'is_active': repo.is_active,
            'scan_status': repo.scan_status,
            'last_scanned_at': repo.last_scanned_at.isoformat() if repo.last_scanned_at else None,
            'file_count': file_count,
            'test_count': test_count,
            'passing_count': passing_count,
            'created_at': repo.created_at.isoformat(),
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_repo(request, repo_id):
    """Get details of a specific repository"""
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
        return Response({
            'id': repo.id,
            'repo_name': repo.repo_name,
            'repo_url': repo.repo_url,
            'created_at': repo.created_at.isoformat(),
        })
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_repo(request):
    full_name = request.data.get('full_name', '').strip()

    if full_name.count('/') != 1:
        return Response(
            {'error': 'Invalid format — use owner/repository-name'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existing active connection
    if GitHubRepo.objects.filter(repo_name=full_name, is_active=True).exists():
        return Response({'error': 'already connected'}, status=status.HTTP_409_CONFLICT)

    # Verify repo exists on GitHub (best-effort, no auth token required for public repos)
    repo_url = f'https://github.com/{full_name}'
    try:
        gh_resp = http_requests.get(
            f'https://api.github.com/repos/{full_name}',
            headers={'Accept': 'application/vnd.github+json'},
            timeout=8,
        )
        if gh_resp.status_code == 404:
            return Response(
                {'error': f'Repository {full_name} not found on GitHub'},
                status=status.HTTP_404_NOT_FOUND
            )
    except http_requests.RequestException:
        pass  # Offline / rate-limited — proceed anyway

    webhook_secret = request.data.get('webhook_secret') or secrets.token_hex(32)

    repo = GitHubRepo.objects.create(
        repo_name=full_name,
        repo_url=repo_url,
        webhook_secret=webhook_secret,
        is_active=True,
        scan_status='pending',
    )

    # Trigger initial repo scan asynchronously
    from apps.ai_engine.tasks import process_initial_repo_scan
    process_initial_repo_scan.delay(repo.id)

    return Response({
        'id': repo.id,
        'full_name': repo.repo_name,
        'repo_url': repo.repo_url,
        'webhook_secret': webhook_secret,
        'scan_status': repo.scan_status,
        'created_at': repo.created_at.isoformat(),
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def disconnect_repo(request, repo_id):
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)
    repo.is_active = False
    repo.save(update_fields=['is_active'])
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def repo_status(request, repo_id):
    """Real-time scan status for a single repository."""
    from apps.ai_engine.models import CodeFile, TestFile
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)

    file_count = CodeFile.objects.filter(repo=repo).count()
    test_count = TestFile.objects.filter(code_file__repo=repo).count()
    passing_count = TestFile.objects.filter(code_file__repo=repo, is_passing=True).count()

    return Response({
        'id': repo.id,
        'full_name': repo.repo_name,
        'scan_status': repo.scan_status,
        'last_scanned_at': repo.last_scanned_at.isoformat() if repo.last_scanned_at else None,
        'file_count': file_count,
        'test_count': test_count,
        'passing_count': passing_count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rescan_repo(request, repo_id):
    """Re-queue an initial scan for a single repo."""
    try:
        repo = GitHubRepo.objects.get(id=repo_id, is_active=True)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)

    repo.scan_status = 'pending'
    repo.save(update_fields=['scan_status'])

    from apps.ai_engine.tasks import process_initial_repo_scan
    process_initial_repo_scan.delay(repo.id)

    return Response(
        {'status': 'queued', 'repo_id': repo.id, 'scan_status': 'pending'},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rescan_all(request):
    """Re-queue scans for every active repository."""
    from apps.ai_engine.tasks import process_initial_repo_scan
    repos = GitHubRepo.objects.filter(is_active=True)
    queued = []
    for repo in repos:
        repo.scan_status = 'pending'
        repo.save(update_fields=['scan_status'])
        process_initial_repo_scan.delay(repo.id)
        queued.append(repo.id)

    return Response(
        {'status': 'queued', 'repos_queued': len(queued), 'repo_ids': queued},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'service': 'zero-touch-test-engine'})

# Made with Bob
