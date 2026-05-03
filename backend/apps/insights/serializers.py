from rest_framework import serializers
from .models import TestOutcome, DevInsight, PainPoint


class TestOutcomeSerializer(serializers.ModelSerializer):
    test_file_path = serializers.CharField(source='test_file.code_file.file_path', read_only=True)
    
    class Meta:
        model = TestOutcome
        fields = ['id', 'test_file', 'test_file_path', 'execution_time', 'passed', 
                  'failed_count', 'error_message', 'coverage_percentage', 'executed_at']


class DevInsightSerializer(serializers.ModelSerializer):
    repo_name = serializers.CharField(source='repo.repo_name', read_only=True)
    
    class Meta:
        model = DevInsight
        fields = ['id', 'repo', 'repo_name', 'date', 'tests_generated', 'tests_passed',
                  'tests_failed', 'avg_execution_time', 'code_coverage', 'files_analyzed']


class PainPointSerializer(serializers.ModelSerializer):
    repo_name = serializers.CharField(source='repo.repo_name', read_only=True)
    
    class Meta:
        model = PainPoint
        fields = ['id', 'repo', 'repo_name', 'category', 'description', 'file_path',
                  'occurrence_count', 'first_seen', 'last_seen', 'resolved']

# Made with Bob