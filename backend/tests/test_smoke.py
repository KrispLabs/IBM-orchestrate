import pytest

@pytest.mark.django_db
def test_database_connection():
    from django.db import connection
    assert connection is not None

@pytest.mark.django_db  
def test_github_integration_app_loads():
    from apps.github_integration.models import GitHubRepo
    assert GitHubRepo is not None

# Made with Bob
