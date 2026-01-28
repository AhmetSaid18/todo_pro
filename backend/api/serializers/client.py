from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Client

class ClientSerializer(AgencyModelSerializer):
    """Client serializer"""
    project_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'agency']
    
    def get_project_count(self, obj):
        return obj.projects.count() if hasattr(obj, 'projects') else 0
