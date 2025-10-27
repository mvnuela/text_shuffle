from django.db import models

class FileStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    DONE = 'done', 'Done'
    FAILED = 'failed', 'Failed'