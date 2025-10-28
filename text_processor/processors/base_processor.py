from django.db import transaction
from abc import ABC, abstractmethod
import os, uuid, logging
from text_processor.models.file_status_choices import FileStatus

logger = logging.getLogger(__name__)

class BaseFileProcessor(ABC):
    """
    Abstract base class for all file processors in the system.

    This class defines a common processing workflow and enforces a unified interface
    for handling text-based files. It manages file status updates, error handling,
    and output file generation. Subclasses must implement the `_process_file()` method,
    which performs the actual transformation logic for a specific file type.

    Attributes:
        file_extension (str):
            Required class attribute that defines the file extension handled
            by the processor (e.g. ".txt", ".csv"). Each subclass must provide
            a valid, non-empty string starting with a dot.

        text_file (TextFile):
            Instance of a Django model representing the file being processed.
            It must expose at least:
              - `original_file.path` — absolute path to the uploaded file.
              - `status` and `error_message` — database fields updated during processing.

    Raises:
        TypeError:
            If a subclass does not define a valid `file_extension`.
    """

    file_extension: str = None

    def __init_subclass__(cls, **kwargs):
        """
        Validate subclass configuration at definition time.

        Ensures that every subclass defines a valid `file_extension` attribute.
        A valid extension must:
          - Be a string.
          - Start with a dot ('.').
          - Have at least one character after the dot.

        Args:
            **kwargs: Optional keyword arguments passed during subclass creation.

        Raises:
            TypeError: If `file_extension` is missing or invalid.
        """
        super().__init_subclass__(**kwargs)
        ext = getattr(cls, "file_extension", None)
        if not isinstance(ext, str) or not ext.startswith(".") or len(ext) < 2:
            raise TypeError(
                f"{cls.__name__} must define a valid 'file_extension' "
                f"(e.g. '.txt', '.csv'), got: {ext!r}"
            )

    def __init__(self, text_file):
        """
        Initialize the processor with a given TextFile instance.

        Args:
            text_file (TextFile): Django model instance representing the file
                to be processed.
        """
        self.text_file = text_file

    def _update_status(self, status, error_message=None):
        """
        Safely update the file's processing status in the database.

        This method uses a transaction to avoid partial updates. It also truncates
        the error message to 500 characters to fit the database field.

        Args:
            status (FileStatus): New status to assign (e.g. PROCESSING, DONE, FAILED).
            error_message (str, optional): Description of an error if applicable.
        """
        self.text_file.status = status
        if error_message:
            self.text_file.error_message = error_message[:500]
        with transaction.atomic():
            self.text_file.save(update_fields=['status', 'error_message'])

    def process(self):
        """
        Execute the complete file processing workflow.

        This template method encapsulates the common sequence:
          1. Create an output directory if it doesn't exist.
          2. Generate a unique output filename.
          3. Update the file status to PROCESSING.
          4. Delegate processing to `_process_file()`.
          5. On success, mark the file as DONE and return the relative result path.
          6. On error, mark the file as FAILED and log the exception.

        Returns:
            str: Relative path to the processed result file (e.g. "results/result_123.csv").

        Raises:
            Exception: Any exception raised by `_process_file()` is re-raised
                after updating the file status and logging the error.
        """
        input_path = self.text_file.original_file.path
        output_dir = os.path.join("media", "results")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"result_{self.text_file.id}_{uuid.uuid4()}{self.file_extension}"
        output_path = os.path.join(output_dir, output_filename)

        self._update_status(FileStatus.PROCESSING)

        try:
            self._process_file(input_path, output_path)
            self._update_status(FileStatus.DONE)
            return f"results/{output_filename}"

        except Exception as e:
            logger.exception(f"Processing failed for file {self.text_file.id}: {e}")
            self._update_status(FileStatus.FAILED, str(e))
            raise

    @abstractmethod
    def _process_file(self, input_path, output_path):
        """
        Process the content of a single file.

        Subclasses must implement this method to define how the file should
        be transformed. The implementation is responsible for reading from
        `input_path` and writing the processed data to `output_path`.

        Args:
            input_path (str): Absolute path to the input file.
            output_path (str): Absolute path where the processed output should be saved.

        Raises:
            Exception: Implementations should raise exceptions to signal processing failures.
        """
        pass
