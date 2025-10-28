# Text Shuffle Project

Text Shuffle is a Django web application that allows uploading text files and processing them using various file processors.
The processing involves shuffling the middle letters of words. The project uses Docker Compose, PostgreSQL, and Redis.

Text Shuffle is designed to handle large text files efficiently. The application processes files **line by line**, rather than loading the entire file into memory. This means even very large files (hundreds of MBs or more) can be processed without running into memory issues. The file I/O uses buffered reading and writing, which reduces system calls and ensures stable performance.


## Installation & Setup

1. **Clone the repository:**

```bash
git clone <repository_url>
cd text_shuffle
```

2. **Copy the example environment file:**

```bash
cp .env.example .env
```

3. **Build and start the containers:**

```bash
docker-compose up -d --build
```

4. **Apply database migrations:**

```bash
docker-compose run --rm web python manage.py migrate
```

5. **Create a superuser :**

```bash
docker-compose run --rm web python manage.py createsuperuser
```

6. **Access the application:**
   Open your browser at `http://localhost:8000`.

---

## Adding a New File Type

To support a new file type in the system, follow these steps:

1. **Create a new processor file** in `text_processor/processors/`, for example `my_file_processor.py`.

2. **Define a processor class** inheriting from `BaseFileProcessor`:

```python
from text_processor.processors.base_processor import BaseFileProcessor

class MyFileProcessor(BaseFileProcessor):
    # Required class attribute defining the file extension
    file_extension = ".myext"

    def _process_file(self, input_path, output_path):
        """
        Template method defining how the file should be processed.

        Args:
            input_path (str): Absolute path to the input file.
            output_path (str): Absolute path to save the processed file.
        """
        with open(input_path, "r") as f_in, open(output_path, "w") as f_out:
            for line in f_in:
                f_out.write(line.upper())  # example transformation
```

3. **Automatic registration:**
   The new processor class will be automatically discovered and registered by `FileProcessorFactory` when the application starts, thanks to the `autodiscover_processors()` method. No additional configuration is needed.

4. **Requirements:**

   * `file_extension` must be a valid string starting with a dot and containing at least one character.
   * `_process_file(input_path, output_path)` must implement the actual file transformation logic.
   * This is a **template method**, meaning that `BaseFileProcessor` provides the overall processing workflow (status updates, output path handling, error logging), and `_process_file` only needs to define the specific transformation.

