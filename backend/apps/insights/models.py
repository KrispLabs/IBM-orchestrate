from django.db import models
from apps.github_integration.models import GitHubRepo
from apps.ai_engine.models import TestFile


class TestOutcome(models.Model):
    """Track test execution outcomes for learning engine"""
    test_file = models.ForeignKey(
        TestFile,
        on_delete=models.CASCADE,
        related_name='outcomes'
    )
    execution_time = models.FloatField(help_text='Test execution time in seconds')
    passed = models.BooleanField(default=False)
    failed_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    coverage_percentage = models.FloatField(default=0.0)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-executed_at']

    def __str__(self):
        return f"Outcome for {self.test_file.code_file.file_path} - {'Passed' if self.passed else 'Failed'}"


class DevInsight(models.Model):
    """Aggregated insights for developer productivity"""
    repo = models.ForeignKey(
        GitHubRepo,
        on_delete=models.CASCADE,
        related_name='insights'
    )
    date = models.DateField()
    tests_generated = models.IntegerField(default=0)
    tests_passed = models.IntegerField(default=0)
    tests_failed = models.IntegerField(default=0)
    avg_execution_time = models.FloatField(default=0.0)
    code_coverage = models.FloatField(default=0.0)
    files_analyzed = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['repo', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Insights for {self.repo.repo_name} on {self.date}"


class PainPoint(models.Model):
    """Track common pain points and patterns"""
    CATEGORY_CHOICES = [
        ('test_failure', 'Test Failure'),
        ('slow_execution', 'Slow Execution'),
        ('low_coverage', 'Low Coverage'),
        ('flaky_test', 'Flaky Test'),
    ]
    
    repo = models.ForeignKey(
        GitHubRepo,
        on_delete=models.CASCADE,
        related_name='pain_points'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    file_path = models.CharField(max_length=500)
    occurrence_count = models.IntegerField(default=1)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-occurrence_count', '-last_seen']

    def __str__(self):
        return f"{self.category} in {self.file_path}"

# Made with Bob
