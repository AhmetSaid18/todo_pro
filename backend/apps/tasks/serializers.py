from rest_framework import serializers
from apps.core.serializers import AgencyModelSerializer
from apps.tasks.models import Task
from apps.users.serializers import UserListSerializer

class TaskSerializer(AgencyModelSerializer):
    """
    Task Serializer.
    """
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'agency']

    def validate_project(self, value):
        # Güvenlik: Kullanıcı sadece kendi ajansının projesine task ekleyebilir.
        user = self.context['request'].user
        if value.agency != user.current_agency:
            raise serializers.ValidationError("Bu projeye erişiminiz yok.")
        return value
