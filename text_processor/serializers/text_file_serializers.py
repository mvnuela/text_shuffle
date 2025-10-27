from rest_framework import serializers
from text_processor.models.models import TextFile
from text_processor.utils.validator_utils import validate_file_extension


class TextFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextFile
        fields = ['id', 'user', 'original_file', 'result_file', 'status', 'updated_at', 'error_message']
        read_only_fields = ['user', 'result_file', 'status']

    def create(self, validated_data):
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        return TextFile.objects.create(user=user, **validated_data)

    def validate_original_file(self, original_file):
        return validate_file_extension(original_file, allowed_ext=['.txt'])
