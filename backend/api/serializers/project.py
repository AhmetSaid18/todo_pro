from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Project
from api.serializers.user import UserListSerializer

class ProjectListSerializer(AgencyModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'status', 'status_display', 'priority', 'start_date', 'end_date', 'team_count', 'created_at']
    
    def get_team_count(self, obj):
        return obj.team_members.count() if hasattr(obj, 'team_members') else 0

class ProjectDetailSerializer(AgencyModelSerializer):
    team_members = UserListSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'agency']
    
    def get_progress_percentage(self, obj):
        tasks = obj.tasks.all()
        total = tasks.count()
        if total == 0:
            return 0
        done = tasks.filter(status='done').count()
        return round((done / total) * 100, 1)

# Alias for compatibility
ProjectSerializer = ProjectDetailSerializer
