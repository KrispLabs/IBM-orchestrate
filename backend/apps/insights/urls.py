from django.urls import path
from . import views

urlpatterns = [
    path('metrics/', views.get_metrics, name='insights-metrics'),
    path('test-health/<int:repo_id>/', views.get_test_health, name='test-health'),
    path('timeline/<int:repo_id>/', views.get_timeline, name='timeline'),
    path('productivity/', views.get_productivity_stats, name='productivity'),
    path('repos/', views.list_repos, name='list-repos'),
    path('repos/<int:repo_id>/', views.get_repo_detail, name='repo-detail'),
]

# Made with Bob