from rest_framework import serializers


def validate_file_extension(file, allowed_ext=None):
    """
    Validates that an uploaded file has an allowed file extension.

    This function checks whether the provided file's name ends with one of the
    allowed extensions. If not, it raises a `serializers.ValidationError`.
    Args:
        file: The uploaded file object
        allowed_ext (list[str], optional):A list of allowed file extensions,
            e.g. ['.txt', '.csv']. Defaults to ['.txt'].

    Raises:
        serializers.ValidationError: If the file's extension is not in the list
        of allowed extensions.

    Returns:
        file: The original uploaded file if validation succeeds.
    Notes:
        - If `allowed_ext` is not provided, it defaults to `['.txt']`.
    """
    if allowed_ext is None:
        allowed_ext = ['.txt']

    filename = file.name.lower()
    if not any(filename.endswith(ext.lower()) for ext in allowed_ext):
        raise serializers.ValidationError(
            f"Invalid file format. Allowed: {', '.join(allowed_ext)}"
        )
    return file

