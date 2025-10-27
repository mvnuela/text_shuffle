from django.contrib import admin
from .models.models import TextFile

@admin.register(TextFile)
class TextFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_file', 'status', 'error_message', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('original_file', 'error_message')

