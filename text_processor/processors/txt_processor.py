import io
from text_processor.utils.text_utils import line_generator, shuffle_text_line
from text_processor.processors.base_processor import BaseFileProcessor

class TxtFileProcessor(BaseFileProcessor):
    file_extension = ".txt"

    def _process_file(self, input_path, output_path):
        with io.open(input_path, 'r', encoding='utf-8') as infile, \
             io.open(output_path, 'w', encoding='utf-8') as outfile:
            for processed_line in line_generator(infile, shuffle_text_line):
                outfile.write(processed_line)
