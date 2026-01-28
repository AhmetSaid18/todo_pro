from api.views.base import AgencyModelViewSet
from api.models import Project
from api.serializers.project import ProjectSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Sum
from django.utils import timezone

class ProjectViewSet(AgencyModelViewSet):
    """
    🎬 PROJE YÖNETİMİ
    
    Workflow:
    1. Müşteriden iş gelir → Proje oluşturulur
    2. Ekip atanır (team members)
    3. Görevler oluşturulur
    4. Takip edilir (progress tracking)
    5. Tamamlanır
    """
    queryset = Project.objects.all().select_related(
        'client', 'created_by'
    ).prefetch_related('team_members', 'tasks', 'equipment_reservations')
    
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'client__company_name']
    filterset_fields = ['status', 'priority', 'client']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'priority']

    def perform_create(self, serializer):
        """Proje oluştururken agency ve creator set et"""
        serializer.save(
            agency=self.request.user.current_agency,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        🔥 Aktif Projeler
        Yöneticinin dashboard'unda göreceği projeler
        """
        active_projects = self.get_queryset().filter(
            status__in=['planned', 'in_progress']
        ).annotate(
            task_count=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status='done'))
        ).order_by('-priority', 'start_date')
        
        serializer = self.get_serializer(active_projects, many=True)
        return Response({
            'count': active_projects.count(),
            'projects': serializer.data
        })

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        📊 Proje İstatistikleri
        - Görev durumları
        - Ekipman kullanımı
        - Budget tracking
        - İlerleme yüzdesi
        """
        project = self.get_object()
        
        # Task stats
        tasks = project.tasks.all()
        task_stats = {
            'total': tasks.count(),
            'not_started': tasks.filter(status='not_started').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'revision_needed': tasks.filter(status='revision_needed').count(),
            'done': tasks.filter(status='done').count(),
            'blocked': tasks.filter(status='blocked').count(),
        }
        
        # Progress percentage
        if task_stats['total'] > 0:
            progress = (task_stats['done'] / task_stats['total']) * 100
        else:
            progress = 0
        
        # Equipment reservations
        equipment_stats = {
            'total_reservations': project.equipment_reservations.count(),
            'active_reservations': project.equipment_reservations.filter(status='active').count()
        }
        
        # Team
        team_stats = {
            'team_size': project.team_members.count(),
            'team_members': [
                {
                    'id': member.id,
                    'name': member.get_full_name() or member.email,
                    'email': member.email
                }
                for member in project.team_members.all()
            ]
        }
        
        # Budget (if exists)
        budget_stats = {
            'estimated_budget': float(project.budget_estimated) if project.budget_estimated else 0,
            'actual_budget': float(project.budget_actual) if project.budget_actual else 0,
        }
        if project.budget_estimated and project.budget_estimated > 0:
            budget_stats['budget_usage_percentage'] = (
                (project.budget_actual or 0) / project.budget_estimated
            ) * 100
        
        return Response({
            'project_id': project.id,
            'project_title': project.title,
            'status': project.status,
            'progress_percentage': round(progress, 1),
            'tasks': task_stats,
            'equipment': equipment_stats,
            'team': team_stats,
            'budget': budget_stats,
            'dates': {
                'start': project.start_date,
                'end': project.end_date,
                'created': project.created_at
            }
        })

    @action(detail=True, methods=['post'])
    def add_team_member(self, request, pk=None):
        """
        👥 Projeye Ekip Üyesi Ekle
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id gerekli'}, status=400)
        
        from api.models import User
        try:
            user = User.objects.get(
                id=user_id,
                memberships__agency=self.request.user.current_agency
            )
            project.team_members.add(user)
            
            # TODO: Notification gönder
            
            return Response({
                'message': f'{user.get_full_name()} projeye eklendi',
                'team_size': project.team_members.count()
            })
        except User.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı'}, status=404)

    @action(detail=True, methods=['post'])
    def remove_team_member(self, request, pk=None):
        """👥 Projeye Ekip Üyesi Çıkar"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id gerekli'}, status=400)
        
        from api.models import User
        try:
            user = User.objects.get(id=user_id)
            project.team_members.remove(user)
            return Response({
                'message': f'{user.get_full_name()} projeden çıkarıldı',
                'team_size': project.team_members.count()
            })
        except User.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı'}, status=404)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        🔄 Proje Durumunu Değiştir
        planned -> in_progress -> review -> completed/cancelled
        """
        project = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['planned', 'in_progress', 'review', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return Response({'error': f'Geçersiz durum. Geçerli olanlar: {valid_statuses}'}, status=400)
        
        old_status = project.status
        project.status = new_status
        
        # Tamamlanıyorsa tarih set et
        if new_status == 'completed':
            project.completed_at = timezone.now()
        
        project.save()
        
        # TODO: Tüm ekibe bildirim gönder
        
        return Response({
            'message': f'Proje durumu {old_status} -> {new_status}',
            'status': new_status,
            'completed_at': project.completed_at if new_status == 'completed' else None
        })

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        📅 Proje Timeline'ı
        Tüm görevleri ve rezervasyonları tarih sırasıyla
        """
        project = self.get_object()
        
        # Tasks timeline
        tasks_timeline = []
        for task in project.tasks.all().order_by('due_date'):
            tasks_timeline.append({
                'type': 'task',
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
                'due_date': task.due_date,
                'priority': task.priority
            })
        
        # Equipment reservations timeline
        reservations_timeline = []
        for res in project.equipment_reservations.all().order_by('start_date'):
            reservations_timeline.append({
                'type': 'equipment_reservation',
                'id': res.id,
                'equipment': res.equipment.name,
                'start_date': res.start_date,
                'end_date': res.end_date,
                'status': res.status,
                'reserved_by': res.reserved_by.get_full_name()
            })
        
        return Response({
            'project': project.title,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'tasks': tasks_timeline,
            'equipment_reservations': reservations_timeline
        })
