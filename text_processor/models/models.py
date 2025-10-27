from django.db import models
from text_processor.models.choices import FileStatus
from django.conf import settings

class TextFile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='text_files',
        null=True,
        blank=True
    )
    original_file = models.FileField(upload_to='uploads/')
    result_file = models.FileField(upload_to='results/', blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=FileStatus.choices,
        default='pending'
    )

    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.original_file.name} ({self.status})"


