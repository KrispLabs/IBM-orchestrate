from django.db import models
from apps.github_integration.models import GitHubRepo
from apps.ai_engine.models import TestFile


class PipelineRun(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]

    repo = models.ForeignKey(GitHubRepo, on_delete=models.CASCADE)
    commit_hash = models.CharField(max_length=100)
    commit_message = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    triggered_by = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.repo.repo_name} - {self.commit_hash[:8]} - {self.status}"


class QualityGate(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE)
    test_coverage = models.FloatField(default=0.0)
    tests_passed = models.IntegerField(default=0)
    tests_failed = models.IntegerField(default=0)
    coverage_threshold = models.FloatField(default=80.0)
    passed = models.BooleanField(default=False)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quality Gate for {self.pipeline_run} - {'Passed' if self.passed else 'Failed'}"


class BuildResult(models.Model):
    pipeline_run = models.OneToOneField(PipelineRun, on_delete=models.CASCADE)
    test_file = models.ForeignKey(TestFile, null=True, blank=True, on_delete=models.SET_NULL)
    output_log = models.TextField(blank=True)
    error_log = models.TextField(blank=True)
    duration_seconds = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Build Result for {self.pipeline_run}"

# Made with Bob
