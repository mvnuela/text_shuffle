from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from text_processor.models.models import TextFile
from text_processor.serializers.text_file_serializers import TextFileSerializer
from text_processor.tasks.tasks import process_text_file_task
from django.shortcuts import render

def index(request):
    return render(request, 'text_processor/index.html')


class TextFileUploadView(generics.CreateAPIView):
    """
    API endpoint for uploading text files for processing.

    This endpoint accepts a file upload via multipart/form-data and creates
    a new `TextFile` instance in the database. Once the file is saved,
    a Celery background task (`process_text_file_task`) is triggered
    to process the uploaded file asynchronously line by line.

    The processing task will:
        - Shuffle the inner letters of each word in the text file.
        - Save the processed result as a new output file.
        - Update the processing status in the database.

    Attributes:
        queryset (QuerySet): The queryset of all `TextFile` objects.
        serializer_class (Serializer): The serializer used for validation and creation.
        parser_classes (list): Parser configuration that enables file uploads (multipart).

    Notes:
        - Large files are processed asynchronously to avoid blocking requests.
        - The processing progress and result can be checked via `TextFileDetailView`.
    """
    queryset = TextFile.objects.all()
    serializer_class = TextFileSerializer
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        """
        Saves the uploaded file and triggers asynchronous Celery processing.

        Args:
            serializer (TextFileSerializer): The validated serializer instance.

        Returns:
            None
        """
        instance = serializer.save()
        # Trigger Celery task for background processing
        process_text_file_task.delay(instance.id)


class TextFileDetailView(generics.RetrieveAPIView):
    """
    API endpoint for checking the processing status and downloading results.

    This endpoint retrieves a single `TextFile` record by its ID,
    allowing the client to:
        - Check the current processing status (`pending`, `processing`, `done`, or `failed`).
        - Obtain the URL of the processed result file once available.

    Attributes:
        queryset (QuerySet): The queryset of all `TextFile` objects.
        serializer_class (Serializer): The serializer used for output formatting.

    Notes:
        - If processing is not yet finished, the `result_file` field will be `null`.
        - If an error occurs during processing, the `error_message` will contain details.
    """
    queryset = TextFile.objects.all()
    serializer_class = TextFileSerializer

