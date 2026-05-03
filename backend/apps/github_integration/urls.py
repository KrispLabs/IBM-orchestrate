from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.github_webhook, name='github-webhook'),
    path('health/', views.health_check, name='health-check'),
    path('repos/', views.list_repos, name='list-repos'),
    path('repos/connect/', views.connect_repo, name='connect-repo'),
    path('repos/rescan-all/', views.rescan_all, name='rescan-all'),
    path('repos/<int:repo_id>/', views.get_repo, name='get-repo'),
    path('repos/<int:repo_id>/status/', views.repo_status, name='repo-status'),
    path('repos/<int:repo_id>/rescan/', views.rescan_repo, name='rescan-repo'),
    path('repos/<int:repo_id>/disconnect/', views.disconnect_repo, name='disconnect-repo'),
]

# Made with Bob
