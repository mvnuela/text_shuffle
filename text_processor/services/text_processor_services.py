import os
import logging
from text_processor.processors.file_processor_factory import FileProcessorFactory

logger = logging.getLogger(__name__)

class TextProcessingService:
    """
    High-level service that delegates file processing to the appropriate processor
    based on file extension.
    """

    def __init__(self, text_file):
        self.text_file = text_file

    def process(self):
        """
        Determine the correct processor for the file and execute its processing logic.
        The processor itself handles updating status and error messages.
        """
        try:
            _, ext = os.path.splitext(self.text_file.original_file.name)
            processor_cls = FileProcessorFactory.get_processor(ext)
            processor = processor_cls(self.text_file)

            result_path = processor.process()
            self.text_file.result_file.name = result_path

        except Exception as e:
            logger.exception(f"Processing failed for file {self.text_file.id}: {e}")


        finally:
            self.text_file.save(update_fields=['result_file'])