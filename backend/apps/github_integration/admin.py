from django.contrib import admin
from .models import GitHubRepo, WebhookEvent

@admin.register(GitHubRepo)
class GitHubRepoAdmin(admin.ModelAdmin):
    list_display = ['repo_name', 'repo_url', 'created_at']

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'repo', 'received_at', 'processed']

# Made with Bob
