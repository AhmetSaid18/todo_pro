from rest_framework import serializers
from apps.core.serializers import AgencyModelSerializer
from apps.equipment.models import Equipment

class EquipmentSerializer(AgencyModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['created_by', 'agency', 'qr_code']
