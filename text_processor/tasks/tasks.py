from celery import shared_task
import logging
from django.db import DatabaseError
from text_processor.models.models import TextFile
from text_processor.services.text_processor_services import TextProcessingService
from text_processor.models.file_status_choices import FileStatus

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(IOError, OSError, DatabaseError),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    default_retry_delay=10,  # seconds
)
def process_file_task(self, file_id: int):
    """
    Celery task to asynchronously process a text file of any supported type.

    Retrieves a `TextFile` by ID and runs `TextProcessingService`,
    which automatically selects the correct processor (TXT, CSV, etc.)
    based on file extension.

    The task retries automatically for transient I/O and database errors.
    """

    try:
        text_file = TextFile.objects.get(id=file_id)
    except TextFile.DoesNotExist:
        logger.warning(f"TextFile with ID={file_id} does not exist — skipping task.")
        return

    logger.info(f"Starting asynchronous processing for TextFile ID={file_id} ({text_file.original_file.name}).")

    service = TextProcessingService(text_file)

    try:
        service.process()
        logger.info(f"File ID={file_id} processed successfully (status: DONE).")

    except (IOError, OSError) as e:
        logger.warning(f"I/O or OS error for file ID={file_id}: {e}")
        raise self.retry(exc=e)

    except DatabaseError as e:

        logger.warning(f"Database error while processing file ID={file_id}: {e}")
        raise self.retry(exc=e)

    except Exception as e:

        logger.exception(f"Unexpected error while processing file ID={file_id}: {e}")
        text_file.status = FileStatus.FAILED
        text_file.error_message = str(e)[:500]
        text_file.save(update_fields=['status', 'error_message'])
        logger.error(f"File ID={file_id} marked as FAILED due to unexpected error.")
