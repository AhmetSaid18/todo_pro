from rest_framework import serializers
from apps.core.serializers import AgencyModelSerializer
from apps.projects.models import Project
from apps.users.serializers import UserListSerializer # Bunu da oluşturacağız

class ProjectListSerializer(AgencyModelSerializer):
    """
    Listeleme için hafif serializer.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_team_count = serializers.IntegerField(source='assigned_team.count', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'client_name', 'status', 'status_display', 'priority', 'start_date', 'end_date', 'assigned_team_count']

class ProjectDetailSerializer(AgencyModelSerializer):
    """
    Detay sayfası için full serializer.
    """
    # M2M alanları ID listesi olarak al, okurken detaylı göster (Future improvement)
    assigned_team = serializers.PrimaryKeyRelatedField(many=True, read_only=True) 

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'agency']
