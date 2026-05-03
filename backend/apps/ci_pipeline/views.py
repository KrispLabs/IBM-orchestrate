from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import PipelineRun, QualityGate, BuildResult
from .serializers import PipelineRunSerializer, QualityGateSerializer, BuildResultSerializer


class PipelineRunViewSet(viewsets.ModelViewSet):
    queryset = PipelineRun.objects.all().order_by('-started_at')
    serializer_class = PipelineRunSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        pipeline_run = self.get_object()
        if pipeline_run.status == 'running':
            return Response({'error': 'Pipeline already running'})
        pipeline_run.status = 'running'
        pipeline_run.save()
        return Response({
            'status': 'triggered',
            'pipeline_id': pipeline_run.id
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        pipeline_run = self.get_object()
        result = request.data.get('result', 'passed')
        pipeline_run.status = result
        pipeline_run.completed_at = timezone.now()
        pipeline_run.save()
        return Response({
            'status': 'completed',
            'result': result
        })


class QualityGateViewSet(viewsets.ModelViewSet):
    queryset = QualityGate.objects.all().order_by('-evaluated_at')
    serializer_class = QualityGateSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        pipeline_run_id = request.data.get('pipeline_run_id')
        test_coverage = float(request.data.get('test_coverage', 0))
        tests_passed = int(request.data.get('tests_passed', 0))
        tests_failed = int(request.data.get('tests_failed', 0))
        threshold = float(request.data.get('coverage_threshold', 80.0))

        try:
            pipeline_run = PipelineRun.objects.get(id=pipeline_run_id)
        except PipelineRun.DoesNotExist:
            return Response({'error': 'Pipeline run not found'}, status=status.HTTP_404_NOT_FOUND)

        passed = test_coverage >= threshold and tests_failed == 0

        gate = QualityGate.objects.create(
            pipeline_run=pipeline_run,
            test_coverage=test_coverage,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            coverage_threshold=threshold,
            passed=passed
        )

        return Response({
            'status': 'evaluated',
            'passed': passed,
            'test_coverage': test_coverage,
            'threshold': threshold,
            'gate_id': gate.id
        })


class BuildResultViewSet(viewsets.ModelViewSet):
    queryset = BuildResult.objects.all().order_by('-created_at')
    serializer_class = BuildResultSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def ci_pipeline_health(request):
    return Response({
        'status': 'ok',
        'service': 'ci-pipeline',
        'models': ['PipelineRun', 'QualityGate', 'BuildResult']
    })

# Made with Bob
