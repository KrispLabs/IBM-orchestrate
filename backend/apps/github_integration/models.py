from django.db import models

class GitHubRepo(models.Model):
    repo_name = models.CharField(max_length=255)
    repo_url = models.URLField()
    github_token = models.TextField()
    webhook_secret = models.TextField(blank=True)
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
