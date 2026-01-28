from api.views.base import AgencyModelViewSet
from api.models import Expense, ShootingDay, CallSheet
from api.serializers.finance_schedule import ExpenseSerializer, ShootingDaySerializer, CallSheetSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone

class ExpenseViewSet(AgencyModelViewSet):
    """
    💰 GİDER YÖNETİMİ
    
    Features:
    - Proje giderleri
    - Kategori bazlı tracking
    - Onay süreci
    - Bütçe kontrolü
    """
    queryset = Expense.objects.all().select_related('project', 'created_by')
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'category']
    filterset_fields = ['project', 'category', 'status']
    ordering_fields = ['date', 'amount', 'created_at']

    def perform_create(self, serializer):
        """Gider oluştururken agency ve creator set et"""
        serializer.save(
            agency=self.request.user.current_agency,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        📊 Projeye Göre Giderler
        ?project_id=123
        """
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id gerekli'}, status=400)
        
        expenses = self.get_queryset().filter(project_id=project_id)
        
        # Kategori bazlı breakdown
        by_category = expenses.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        total = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        # Onay durumları
        by_status = {
            'pending': expenses.filter(status='pending').count(),
            'approved': expenses.filter(status='approved').count(),
            'rejected': expenses.filter(status='rejected').count(),
        }
        
        serializer = self.get_serializer(expenses, many=True)
        
        return Response({
            'project_id': project_id,
            'total_expense': float(total),
            'by_category': list(by_category),
            'by_status': by_status,
            'expenses': serializer.data
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """✅ Gideri Onayla (Yönetici)"""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response({'error': 'Sadece beklemedeki giderler onaylanabilir'}, status=400)
        
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.save()
        
        # Budget'a ekle
        if expense.project:
            project = expense.project
            if project.budget_actual:
                project.budget_actual += expense.amount
            else:
                project.budget_actual = expense.amount
            project.save()
        
        return Response({
            'status': 'approved',
            'message': f'{expense.amount} TL gider onaylandı'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """❌ Gideri Reddet"""
        expense = self.get_object()
        rejection_note = request.data.get('note', '')
        
        if expense.status != 'pending':
            return Response({'error': 'Sadece beklemedeki giderler reddedilebilir'}, status=400)
        
        expense.status = 'rejected'
        expense.notes = f"[Reddedildi] {rejection_note}\n" + (expense.notes or "")
        expense.save()
        
        return Response({
            'status': 'rejected',
            'message': 'Gider reddedildi'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        📊 Gider İstatistikleri (Agency-wide)
        """
        # Toplam giderler
        total = self.get_queryset().filter(
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Bu ay
        from datetime import datetime, timedelta
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        this_month = self.get_queryset().filter(
            status='approved',
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Kategori breakdown
        by_category = self.get_queryset().filter(
            status='approved'
        ).values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Pending approvals
        pending_count = self.get_queryset().filter(status='pending').count()
        
        return Response({
            'total_expenses': float(total),
            'this_month': float(this_month),
            'by_category': list(by_category),
            'pending_approvals': pending_count
        })


class ShootingDayViewSet(AgencyModelViewSet):
    """
    🎬 ÇEKİM GÜNLERİ
    
    Günlük çekim planlaması
    """
    queryset = ShootingDay.objects.all().select_related('project')
    serializer_class = ShootingDaySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'status']
    ordering_fields = ['shoot_date', 'created_at']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        🗓️ Yaklaşan Çekimler
        Önümüzdeki 7 gün
        """
        from datetime import timedelta
        today = timezone.now().date()
        week_later = today + timedelta(days=7)
        
        upcoming = self.get_queryset().filter(
            shoot_date__gte=today,
            shoot_date__lte=week_later
        ).order_by('shoot_date')
        
        serializer = self.get_serializer(upcoming, many=True)
        
        return Response({
            'count': upcoming.count(),
            'shooting_days': serializer.data
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """✅ Çekimi Tamamla"""
        shooting_day = self.get_object()
        
        shooting_day.status = 'completed'
        shooting_day.actual_crew = request.data.get('actual_crew', '')
        shooting_day.notes += f"\n[Tamamlandı: {timezone.now()}]"
        shooting_day.save()
        
        return Response({
            'status': 'completed',
            'message': 'Çekim günü tamamlandı'
        })


class CallSheetViewSet(AgencyModelViewSet):
    """
    📋 CALL SHEET (Çekim Çağrı Formu)
    
    Günlük çekim planı detayları
    """
    queryset = CallSheet.objects.all().select_related('project', 'shooting_day')
    serializer_class = CallSheetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'shooting_day']

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        📄 PDF Olarak İndir
        TODO: PDF generation
        """
        call_sheet = self.get_object()
        
        # TODO: PDF generation logic (ReportLab veya WeasyPrint)
        
        return Response({
            'message': 'PDF generation henüz implement edilmedi',
            'call_sheet_id': call_sheet.id
        })

    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        📅 Bugünkü Call Sheet'ler
        """
        today = timezone.now().date()
        
        today_sheets = self.get_queryset().filter(
            shooting_day__shoot_date=today
        )
        
        serializer = self.get_serializer(today_sheets, many=True)
        
        return Response({
            'date': today,
            'count': today_sheets.count(),
            'call_sheets': serializer.data
        })
