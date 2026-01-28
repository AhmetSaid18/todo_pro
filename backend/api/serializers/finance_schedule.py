from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Expense, ShootingDay, CallSheet

class ExpenseSerializer(AgencyModelSerializer):
    """Expense serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['created_by', 'approved_by', 'approved_at', 'created_at', 'agency', 'status']

class ShootingDaySerializer(AgencyModelSerializer):
    """Shooting Day serializer"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ShootingDay
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'agency']

class CallSheetSerializer(AgencyModelSerializer):
    """Call Sheet serializer"""
    
    class Meta:
        model = CallSheet
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'agency']
