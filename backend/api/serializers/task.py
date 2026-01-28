from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Task
from api.serializers.user import UserListSerializer

class TaskSerializer(AgencyModelSerializer):
    """Task serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'agency']
