from celery import shared_task
import logging
from django.db import DatabaseError
from text_processor.models.models import TextFile
from text_processor.services.services import TextProcessingService

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(IOError, OSError, DatabaseError),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    default_retry_delay=10,  # seconds
)
def process_text_file_task(self, file_id: int):
    """
    Celery task that asynchronously processes a text file.

    This task retrieves a `TextFile` instance by its ID and uses the
    `TextProcessingService` to process it line by line.
    It automatically retries in case of I/O or database errors, and
    updates the file's processing status in the database.

    Args:
        self: Celery task instance (automatically provided by Celery).
        file_id (int): The ID of the `TextFile` model instance to process.

    Raises:
        self.retry: If an I/O or database error occurs (Celery retries automatically).
        Exception: For unexpected errors, which are logged and mark the file as failed.
    """
    try:
        text_file = TextFile.objects.get(id=file_id)
    except TextFile.DoesNotExist:
        logger.warning(f"TextFile with ID {file_id} does not exist — skipping task.")
        return

    logger.info(f"Starting file processing for TextFile ID {file_id} via Celery.")

    service = TextProcessingService(text_file)

    try:
        service.process_file()
        logger.info(f"File processing completed successfully for ID {file_id} (status: DONE).")

    except (IOError, OSError) as e:
        logger.warning(f"I/O error occurred while processing file ID {file_id}: {e}")
        raise self.retry(exc=e)

    except Exception as e:
        logger.exception(f"Unexpected error in Celery task for file ID {file_id}: {e}")
        text_file.status = 'failed'
        text_file.error_message = str(e)
        text_file.save()
        logger.error(f"File ID {file_id} marked as 'failed'. Error: {e}")
