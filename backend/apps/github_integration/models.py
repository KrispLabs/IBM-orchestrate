from django.db import models

class GitHubRepo(models.Model):
    SCAN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scanning', 'Scanning'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    repo_name = models.CharField(max_length=255)
    repo_url = models.URLField(blank=True)
    github_token = models.TextField(blank=True)
    webhook_secret = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    scan_status = models.CharField(
        max_length=20,
        choices=SCAN_STATUS_CHOICES,
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.repo_name

class WebhookEvent(models.Model):
    repo = models.ForeignKey(GitHubRepo, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event_type} - {self.received_at}"

# Made with Bob
