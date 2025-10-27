from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from text_processor.models.models import TextFile

class TextFileUploadAPITest(APITestCase):
    def test_upload_text_file(self):

        test_content = b"Hello world\nThis is a test file"
        test_file = SimpleUploadedFile("test.txt", test_content, content_type="text/plain")

        url = reverse('file-upload')
        response = self.client.post(url, {'original_file': test_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(TextFile.objects.count(), 1)

        text_file = TextFile.objects.first()
        self.assertTrue(text_file.original_file.name.endswith('.txt'))
        self.assertEqual(text_file.status, 'pending')

    def test_get_text_file_detail(self):
        text_file = TextFile.objects.create(
            original_file='uploads/test.txt',
            status='done',
            result_file='results/result_test.txt'
        )

        url = reverse('file-detail', args=[text_file.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], text_file.id)
        self.assertEqual(response.data['status'], 'done')


class TextFileUploadInvalidFormatAPITest(APITestCase):
    def test_reject_non_text_file(self):
        fake_image = SimpleUploadedFile(
            "image.jpg",
            b"\xff\xd8\xff\xe0\x00\x10JFIF",
            content_type="image/jpeg"
        )

        url = reverse('file-upload')
        response = self.client.post(url, {'original_file': fake_image}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TextFile.objects.count(), 0)
        self.assertIn('original_file', response.data)
        self.assertIn('Invalid file format', response.data['original_file'][0])

