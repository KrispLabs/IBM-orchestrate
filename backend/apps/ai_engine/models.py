from django.db import models
from apps.github_integration.models import GitHubRepo


class CodeFile(models.Model):
    repo = models.ForeignKey(GitHubRepo, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    file_content = models.TextField()
    language = models.CharField(max_length=50, default='python')
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.repo.repo_name} - {self.file_path}"

    class Meta:
        unique_together = ['repo', 'file_path']


class TestFile(models.Model):
    code_file = models.OneToOneField(
        CodeFile,
        on_delete=models.CASCADE,
        related_name='test_file'
    )
    test_content = models.TextField()
    generated_by_ai = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_passing = models.BooleanField(default=False)

    def __str__(self):
        return f"Tests for {self.code_file.file_path}"


class ChangeEvent(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    code_file = models.ForeignKey(
        CodeFile,
        on_delete=models.CASCADE,
        related_name='change_events'
    )
    previous_content = models.TextField()
    new_content = models.TextField()
    commit_hash = models.CharField(max_length=100, blank=True)
    commit_message = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    detected_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Change in {self.code_file.file_path} - {self.status}"

# Made with Bob
