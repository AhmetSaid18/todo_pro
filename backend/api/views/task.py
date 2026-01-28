from api.views.base import AgencyModelViewSet
from api.models import Task
from api.serializers.task import TaskSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

class TaskViewSet(AgencyModelViewSet):
    """
    🎬 Task (Görev) Yönetimi
    
    Workflow Durumları:
    - not_started: Başlanmadı
    - in_progress: Devam ediyor (Çalışan lokasyona gitti, işe başladı)
    - in_review: Gözden geçirmede (Fatih kontrol ediyor)
    - revision_needed: Revizyon gerekiyor
    - done: Tamamlandı
    - blocked: Engellendi (Bağımlılık var)
    """
    queryset = Task.objects.all().select_related(
        'project', 'assigned_to', 'created_by'
    ).prefetch_related('equipment_used')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['project', 'status', 'priority', 'assigned_to']
    ordering_fields = ['due_date', 'priority', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        # Sadece kendi görevlerimi göster (member ise)
        if self.request.GET.get('my_tasks') == 'true':
            qs = qs.filter(assigned_to=self.request.user)
        return qs

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        🏁 Görevi Başlat
        Çalışan: "Lokasyona gittim, çekime başlıyorum"
        """
        task = self.get_object()
        
        if task.status != 'not_started':
            return Response({'error': 'Görev zaten başlatılmış'}, status=400)
        
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        
        # TODO: Notification -> Projeye atanan yöneticilere bildirim
        
        return Response({
            'status': 'in_progress',
            'message': f'"{task.title}" görevi başlatıldı',
            'started_at': task.started_at
        })

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """
        📤 Gözden Geçirme İçin Gönder
        Çalışan: "İşim bitti, kontrol edin"
        """
        task = self.get_object()
        
        if task.status != 'in_progress':
            return Response({'error': 'Sadece devam eden görevler gönderilebilir'}, status=400)
        
        # Opsiyonel: Dosya kontrolü (en az 1 dosya yüklenmeli mi?)
        if request.data.get('require_files') and not task.files.exists():
            return Response({'error': 'En az bir dosya yüklemelisiniz'}, status=400)
        
        task.status = 'in_review'
        task.submitted_at = timezone.now()
        task.save()
        
        # TODO: Yöneticiye (created_by veya project owner) bildirim
        
        return Response({
            'status': 'in_review',
            'message': 'Görev gözden geçirilmeye gönderildi',
            'submitted_at': task.submitted_at
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        ✅ Görevi Onayla (Yönetici)
        Fatih Abi: "Süper olmuş, onaylandı!"
        """
        task = self.get_object()
        
        if task.status != 'in_review':
            return Response({'error': 'Sadece gözden geçirimdeki görevler onaylanabilir'}, status=400)
        
        task.status = 'done'
        task.completed_at = timezone.now()
        task.save()
        
        # Email gönder (Celery async)
        from api.tasks import send_task_approved_email
        send_task_approved_email.delay(task.id)
        
        # Notification service
        from api.services.notification import NotificationService
        NotificationService.notify_task_approved(task)

        return Response({
            'status': 'done',
            'message': f'"{task.title}" başarıyla tamamlandı!',
            'completed_at': task.completed_at
        })

    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        """
        🔄 Revizyon İste (Yönetici)
        Fatih Abi: "Şunu değiştir, tekrar yap"
        """
        task = self.get_object()
        
        if task.status != 'in_review':
            return Response({'error': 'Sadece gözden geçirimdeki görevler için revizyon istenebilir'}, status=400)
        
        revision_note = request.data.get('revision_note', '')
        if not revision_note:
            return Response({'error': 'Revizyon notu zorunlu'}, status=400)
        
        task.status = 'revision_needed'
        task.revision_notes = f"[{timezone.now()}] {revision_note}\n" + (task.revision_notes or "")
        task.save()
        
        # Email gönder (Celery async)
        from api.tasks import send_task_revision_email
        send_task_revision_email.delay(task.id)
        
        # Notification service
        from api.services.notification import NotificationService
        NotificationService.notify_task_revision(task)
        
        return Response({
            'status': 'revision_needed',
            'message': 'Revizyon talebi gönderildi',
            'revision_note': revision_note
        })

    @action(detail=True, methods=['post'])
    def resubmit(self, request, pk=None):
        """
        🔁 Revizyonu Tamamla ve Tekrar Gönder
        Çalışan: "Düzelttim, tekrar bakın"
        """
        task = self.get_object()
        
        if task.status != 'revision_needed':
            return Response({'error': 'Görev revizyon durumunda değil'}, status=400)
        
        task.status = 'in_review'
        task.resubmitted_at = timezone.now()
        task.save()
        
        return Response({
            'status': 'in_review',
            'message': 'Görev tekrar gözden geçirilmeye gönderildi'
        })

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """
        🚫 Görevi Engelle
        Bir bağımlılık veya sorun var
        """
        task = self.get_object()
        block_reason = request.data.get('block_reason', '')
        
        task.status = 'blocked'
        task.block_reason = block_reason
        task.save()
        
        return Response({
            'status': 'blocked',
            'block_reason': block_reason
        })

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """✅ Engeli Kaldır"""
        task = self.get_object()
        
        if task.status != 'blocked':
            return Response({'error': 'Görev zaten engellenmiş durumda değil'}, status=400)
        
        task.status = 'not_started'
        task.block_reason = None
        task.save()
        
        return Response({'status': 'not_started', 'message': 'Görev engeli kaldırıldı'})

    @action(detail=False, methods=['get'])
    def my_active(self, request):
        """
        📋 Benim Aktif Görevlerim (Mobil için)
        Çalışanın bugün ve yakın zamandaki görevleri
        """
        my_tasks = self.get_queryset().filter(
            assigned_to=request.user,
            status__in=['not_started', 'in_progress', 'revision_needed']
        ).order_by('due_date')
        
        serializer = self.get_serializer(my_tasks, many=True)
        return Response({
            'count': my_tasks.count(),
            'tasks': serializer.data
        })

    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """
        📊 Gözden Geçirilmeyi Bekleyenler (Yönetici için)
        Fatih Abi'nin kontrol etmesi gerekenler
        """
        pending = self.get_queryset().filter(
            status='in_review'
        ).order_by('submitted_at')
        
        serializer = self.get_serializer(pending, many=True)
        return Response({
            'count': pending.count(),
            'tasks': serializer.data
        })
