import csv
import os
import uuid
import logging
from text_processor.models.file_status_choices import FileStatus
from text_processor.processors.base_processor import BaseFileProcessor
from text_processor.utils.text_utils import shuffle_text_line

logger = logging.getLogger(__name__)

import csv
from text_processor.utils.text_utils import shuffle_text_line
from text_processor.processors.base_processor import BaseFileProcessor

class CSVFileProcessor(BaseFileProcessor):
    file_extension = ".csv"

    def _process_file(self, input_path, output_path):
        with open(input_path, "r", encoding="utf-8", newline="") as infile, \
             open(output_path, "w", encoding="utf-8", newline="") as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                processed_row = [shuffle_text_line(cell) for cell in row]
                writer.writerow(processed_row)
