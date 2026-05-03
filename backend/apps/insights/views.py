from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import TestOutcome, DevInsight, PainPoint
from .serializers import TestOutcomeSerializer, DevInsightSerializer, PainPointSerializer
from apps.github_integration.models import GitHubRepo
from apps.ai_engine.models import TestFile, CodeFile


@api_view(['GET'])
@permission_classes([AllowAny])
def get_metrics(request):
    """Get overall metrics for dashboard"""
    repo_id = request.query_params.get('repo')
    
    # Filter by repo if provided
    test_files = TestFile.objects.all()
    code_files = CodeFile.objects.all()
    
    if repo_id:
        test_files = test_files.filter(code_file__repo_id=repo_id)
        code_files = code_files.filter(repo_id=repo_id)
    
    # Calculate metrics
    total_tests = test_files.count()
    passing_tests = test_files.filter(is_passing=True).count()
    files_analyzed = code_files.count()
    
    # Calculate coverage (simplified)
    coverage = (passing_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Test status distribution
    test_status = [
        {'status': 'Passing', 'count': passing_tests},
        {'status': 'Failing', 'count': total_tests - passing_tests},
    ]
    
    return Response({
        'total_tests': total_tests,
        'passing_tests': passing_tests,
        'coverage': round(coverage, 2),
        'files_analyzed': files_analyzed,
        'test_status': test_status,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_test_health(request, repo_id):
    """Get test health metrics for a specific repository"""
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)
    
    test_files = TestFile.objects.filter(code_file__repo=repo)
    total_tests = test_files.count()
    passing = test_files.filter(is_passing=True).count()
    
    # Get recent outcomes
    recent_outcomes = TestOutcome.objects.filter(
        test_file__code_file__repo=repo
    ).order_by('-executed_at')[:10]
    
    avg_coverage = recent_outcomes.aggregate(Avg('coverage_percentage'))['coverage_percentage__avg'] or 0
    
    return Response({
        'total_tests': total_tests,
        'passing': passing,
        'failing': total_tests - passing,
        'coverage': round(avg_coverage, 2),
        'recent_outcomes': TestOutcomeSerializer(recent_outcomes, many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_timeline(request, repo_id):
    """Get activity timeline for a repository"""
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get recent change events
    from apps.ai_engine.models import ChangeEvent
    
    events = ChangeEvent.objects.filter(
        code_file__repo=repo
    ).order_by('-detected_at')[:20]
    
    timeline = []
    for event in events:
        timeline.append({
            'title': f"Code change in {event.code_file.file_path}",
            'description': event.commit_message or 'No commit message',
            'status': 'completed' if event.status == 'completed' else event.status,
            'timestamp': event.detected_at.isoformat(),
        })
    
    return Response(timeline)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_productivity_stats(request):
    """Get productivity statistics across all repos"""
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    # Aggregate directly from TestFile creation dates (DevInsight requires Beat scheduler)
    timeline_qs = (
        TestFile.objects
        .filter(created_at__date__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(tests=Count('id'))
        .order_by('date')
    )

    timeline = [
        {'date': row['date'].strftime('%Y-%m-%d'), 'tests': row['tests']}
        for row in timeline_qs
    ]

    pain_points = PainPoint.objects.filter(resolved=False).order_by('-occurrence_count')[:10]

    return Response({
        'timeline': timeline,
        'pain_points': PainPointSerializer(pain_points, many=True).data,
        'total_tests_generated': TestFile.objects.count(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_repos(request):
    """List all connected repositories with basic stats"""
    repos = GitHubRepo.objects.all()
    
    repo_data = []
    for repo in repos:
        test_count = TestFile.objects.filter(code_file__repo=repo).count()
        passing_count = TestFile.objects.filter(code_file__repo=repo, is_passing=True).count()
        
        repo_data.append({
            'id': repo.id,
            'repo_name': repo.repo_name,
            'repo_url': repo.repo_url,
            'created_at': repo.created_at.isoformat(),
            'test_count': test_count,
            'passing_count': passing_count,
        })
    
    return Response(repo_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_repo_detail(request, repo_id):
    """Get detailed information about a specific repository"""
    try:
        repo = GitHubRepo.objects.get(id=repo_id)
    except GitHubRepo.DoesNotExist:
        return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)
    
    test_files = TestFile.objects.filter(code_file__repo=repo)
    
    return Response({
        'id': repo.id,
        'repo_name': repo.repo_name,
        'repo_url': repo.repo_url,
        'created_at': repo.created_at.isoformat(),
        'test_count': test_files.count(),
        'passing_count': test_files.filter(is_passing=True).count(),
    })

# Made with Bob
