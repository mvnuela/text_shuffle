from django.urls import path
from .views.text_file_views import TextFileUploadView, TextFileDetailView, index

urlpatterns = [
    path('', index, name='index'),
    path('upload/', TextFileUploadView.as_view(), name='file-upload'),
    path('file/<int:pk>/', TextFileDetailView.as_view(), name='file-detail'),
]
