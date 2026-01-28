from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import AgencyMembership

User = get_user_model()

class UserListSerializer(serializers.ModelSerializer):
    """
    Dropdownlarda vs. kullanıcıyı listelemek için.
    """
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar', 'title', 'role']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    
    def get_role(self, obj):
        # Request context'ten ajansı bul, rolünü getir.
        # Bu kısım biraz tricky, şimdilik basit geçiyorum.
        return "Member"
