from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from text_processor.utils.validator_utils import validate_file_extension

def test_validate_file_extension_valid_txt():
    file = SimpleUploadedFile("test.txt", b"dummy")
    assert validate_file_extension(file, ['.txt']) == file

def test_validate_file_extension_invalid_extension():
    file = SimpleUploadedFile("test.pdf", b"dummy")
    try:
        validate_file_extension(file, ['.txt', '.csv'])
    except ValidationError as e:
        assert "Allowed" in str(e)
    else:
        assert False, "Expected ValidationError for invalid extension"
