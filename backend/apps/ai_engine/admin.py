from django.contrib import admin
from .models import CodeFile, TestFile, ChangeEvent


@admin.register(CodeFile)
class CodeFileAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'repo', 'language', 'last_modified']
    list_filter = ['language', 'repo']
    search_fields = ['file_path']


@admin.register(TestFile)
class TestFileAdmin(admin.ModelAdmin):
    list_display = ['code_file', 'generated_by_ai', 'is_passing', 'last_updated']
    list_filter = ['generated_by_ai', 'is_passing']


@admin.register(ChangeEvent)
class ChangeEventAdmin(admin.ModelAdmin):
    list_display = ['code_file', 'status', 'commit_hash', 'detected_at']
    list_filter = ['status']
    search_fields = ['commit_hash', 'commit_message']

# Made with Bob
