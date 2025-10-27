import os
import io
import uuid
import logging
from django.db import transaction
from text_processor.models.models import TextFile
from text_processor.utils.text_utils import line_generator, shuffle_text_line
from text_processor.models.choices import FileStatus

logger = logging.getLogger(__name__)


class TextProcessingService:
    """
    A service for processing large text files line by line in a safe and transactional way.

    This class is designed to handle heavy text processing workloads where a file must be
    read and transformed efficiently without loading the entire file into memory.
    It integrates with Django's ORM and is safe for use in Celery background tasks.

    The service reads the source file, processes each line using a given text transformation
    (by default, `shuffle_text_line`), and writes the processed output to a new file.
    It manages file statuses and error logging in the database through `FileStatus` enum values.

    Attributes:
        text_file (TextFile): The `TextFile` model instance representing the file being processed.
    """

    def __init__(self, text_file: TextFile):

        self.text_file = text_file

    def _update_status(self, status: FileStatus, error_message: str = None):
        """
        Safely updates the processing status of the file in the database.

        The update is performed atomically using a database transaction.
        If an error message is provided, it is stored in the `error_message` field.

        Args:
            status (FileStatus): The new processing status (e.g., `PROCESSING`, `DONE`, `FAILED`).
            error_message (str, optional): An optional description of an error that occurred.
        """
        self.text_file.status = status
        if error_message:
            self.text_file.error_message = error_message[:500]  # truncate for safety
        with transaction.atomic():
            self.text_file.save(update_fields=['status', 'error_message'])

    def process_file(self):
        """
        Processes the input file line by line and writes the transformed output to a new file.

        This method:
        - Updates the file's status to `PROCESSING`.
        - Opens the source text file and creates a result file with a unique name.
        - Iterates through the lines of the file using `line_generator`, applying
          the `shuffle_text_line` processor to each line.
        - Writes the processed lines to the output file in a memory-efficient manner.
        - Updates the database record to mark the process as `DONE` on success.
        - Catches and logs I/O or decoding errors, marking the process as `FAILED` if necessary.

        Raises:
            IOError: If the input or output file cannot be opened or written.
            OSError: If an OS-level error occurs (e.g., missing directories, permissions).
            UnicodeDecodeError: If the input file cannot be decoded as UTF-8.
            Exception: For any other unexpected runtime errors.

        Notes:
            - Both input and output files are opened with buffered I/O for performance.
            - The resulting file path is saved in the `result_file` field of the model.
            - The method ensures the final database state is always saved (via `finally` block).
        """
        input_path = self.text_file.original_file.path
        output_dir = os.path.join('media', 'results')
        os.makedirs(output_dir, exist_ok=True)

        unique_id = uuid.uuid4()
        output_filename = f'result_{self.text_file.id}_{unique_id}.txt'
        output_path = os.path.join(output_dir, output_filename)

        self._update_status(FileStatus.PROCESSING)

        try:
            with io.open(input_path, 'r', encoding='utf-8', buffering=16 * 1024) as infile, \
                    io.open(output_path, 'w', encoding='utf-8', buffering=16 * 1024) as outfile:

                for processed_line in line_generator(infile=infile, line_processor=shuffle_text_line):
                    outfile.write(processed_line)

            self.text_file.result_file.name = f'results/{output_filename}'
            self._update_status(FileStatus.DONE)

        except (IOError, OSError, UnicodeDecodeError) as e:
            logger.exception(f"Error while processing file {self.text_file.id}: {e}")
            self._update_status(FileStatus.FAILED, str(e))
            raise

        except Exception as e:
            logger.exception(f"Unexpected error during file processing {self.text_file.id}: {e}")
            self._update_status(FileStatus.FAILED, str(e))
            raise

        finally:
            self.text_file.save()
