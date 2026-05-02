import hashlib
import hmac
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
        WebhookEvent.objects.create(
            repo=repo,
            event_type=event_type,
            payload=payload
        )

    return JsonResponse({'status': 'received', 'event': event_type})


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'service': 'zero-touch-test-engine'})

# Made with Bob
