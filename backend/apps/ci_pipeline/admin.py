from django.contrib import admin
from .models import PipelineRun, QualityGate, BuildResult


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ['repo', 'commit_hash', 'status', 'started_at']
    list_filter = ['status']


@admin.register(QualityGate)
class QualityGateAdmin(admin.ModelAdmin):
    list_display = ['pipeline_run', 'test_coverage', 'passed', 'evaluated_at']
    list_filter = ['passed']


@admin.register(BuildResult)
class BuildResultAdmin(admin.ModelAdmin):
    list_display = ['pipeline_run', 'duration_seconds', 'created_at']

# Made with Bob
