from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/github/', include('apps.github_integration.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/insights/', include('apps.insights.urls')),
]

# Made with Bob
