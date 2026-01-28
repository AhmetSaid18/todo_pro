from rest_framework import serializers
from api.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """Bildirim serializer"""
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'link', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
