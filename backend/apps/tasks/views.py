from apps.core.views import AgencyModelViewSet
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(AgencyModelViewSet):
    queryset = Task.objects.all().order_by('due_date')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'status', 'assigned_to']

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Görevi hızlıca Done/Todo arası değiştirir.
        """
        task = self.get_object()
        if task.status == 'done':
            task.status = 'todo'
        else:
            task.status = 'done'
        task.save()
        return Response({'status': task.status})
