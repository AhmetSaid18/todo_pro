from apps.core.views import AgencyModelViewSet
from apps.projects.models import Project
from apps.projects.serializers import ProjectListSerializer, ProjectDetailSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend # Filtering

class ProjectViewSet(AgencyModelViewSet):
    """
    Project CRUD Endpoints.
    """
    queryset = Project.objects.all().order_by('-updated_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'client_name', 'description']
    ordering_fields = ['start_date', 'budget_estimated']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
