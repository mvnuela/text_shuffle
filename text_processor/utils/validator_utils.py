from rest_framework import serializers
from text_processor.processors.file_processor_factory import FileProcessorFactory

def validate_file_extension(file, allowed_ext=None):
    """
    Validates that an uploaded file has an allowed file extension.
    If `allowed_ext` is not provided, it loads supported extensions
    from the FileProcessorFactory (dynamic discovery).

    Args:
        file: Uploaded file object.
        allowed_ext (list[str], optional): List of allowed file extensions.

    Raises:
        serializers.ValidationError: If the file extension is not allowed.

    Returns:
        file: The original uploaded file if validation succeeds.
    """
    filename = file.name.lower()

    # Determine extension
    if '.' not in filename:
        raise serializers.ValidationError("The uploaded file has no extension.")
    ext = '.' + filename.split('.')[-1]

    # Auto-discover supported extensions from factory if not explicitly provided
    if allowed_ext is None:
        factory = FileProcessorFactory
        if not factory._registry:
            factory._discover_processors()
        allowed_ext = list(factory._registry.keys())

    # Check extension
    if ext not in [e.lower() for e in allowed_ext]:
        raise serializers.ValidationError(
            f"Invalid file format '{ext}'. "
            f"Allowed formats: {', '.join(allowed_ext)}."
        )

    return file
