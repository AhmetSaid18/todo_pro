from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from api.models import AgencyMembership

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Ana user serializer"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 
                  'avatar', 'phone', 'is_active', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined', 'is_active']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar', 'role_name', 'phone']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    
    def get_role_name(self, obj):
        if not obj.current_agency:
            return ""
        membership = obj.memberships.filter(agency=obj.current_agency).first()
        return membership.role.name if membership and membership.role else "Member"

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Kullanıcının kendi profilini güncellemesi için.
    Email değiştirilemez (Güvenlik).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar', 'phone']
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class AgencyMembershipSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = AgencyMembership
        fields = ['id', 'user', 'role_name', 'is_owner', 'is_active', 'joined_at']
