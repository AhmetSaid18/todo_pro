from rest_framework import serializers
from apps.core.serializers import AgencyModelSerializer
from apps.equipment.models import EquipmentCategory

class CategorySerializer(AgencyModelSerializer):
    class Meta:
        model = EquipmentCategory
        fields = '__all__'
