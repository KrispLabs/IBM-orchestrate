from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.github_webhook, name='github-webhook'),
    path('health/', views.health_check, name='health-check'),
]

# Made with Bob
