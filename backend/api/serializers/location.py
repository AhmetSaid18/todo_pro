from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Location

class LocationSerializer(AgencyModelSerializer):
    """Location serializer"""
    
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'agency', 'usage_count']
