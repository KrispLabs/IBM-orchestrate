from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.github_webhook, name='github-webhook'),
    path('health/', views.health_check, name='health-check'),
    path('repos/', views.list_repos, name='list-repos'),
    path('repos/<int:repo_id>/', views.get_repo, name='get-repo'),
]

# Made with Bob
