from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import File

class FileSerializer(AgencyModelSerializer):
    """File serializer"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'created_at', 'agency', 'file_size', 'file_type']
