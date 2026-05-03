from rest_framework import serializers
from .models import PipelineRun, QualityGate, BuildResult


class PipelineRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineRun
        fields = '__all__'
        read_only_fields = ['started_at', 'completed_at']


class QualityGateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityGate
        fields = '__all__'
        read_only_fields = ['evaluated_at']


class BuildResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildResult
        fields = '__all__'
        read_only_fields = ['created_at']

# Made with Bob
