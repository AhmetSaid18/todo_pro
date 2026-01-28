from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import FileTransfer

class FileTransferSerializer(AgencyModelSerializer):
    class Meta:
        model = FileTransfer
        fields = '__all__'
        read_only_fields = ['agency', 'user', 'download_count', 'expires_at', 'total_size_bytes', 'id']
        extra_kwargs = {'password': {'write_only': True}}
