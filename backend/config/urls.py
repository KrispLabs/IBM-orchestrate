from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/github/', include('apps.github_integration.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
]

# Made with Bob
