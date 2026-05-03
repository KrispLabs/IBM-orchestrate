from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pipeline-runs', views.PipelineRunViewSet)
router.register(r'quality-gates', views.QualityGateViewSet)
router.register(r'build-results', views.BuildResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.ci_pipeline_health, name='ci-pipeline-health'),
]

# Made with Bob
