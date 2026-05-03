from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_tests_view, name='generate-tests'),
    path('update/', views.update_tests_view, name='update-tests'),
    path('tests/', views.list_test_files, name='list-test-files'),
    path('tests/<int:test_id>/', views.get_test_file, name='get-test-file'),
    path('repo-overview/<int:repo_id>/', views.repo_overview, name='repo-overview'),
]

# Made with Bob
