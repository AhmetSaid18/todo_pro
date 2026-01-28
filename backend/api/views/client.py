from api.views.base import AgencyModelViewSet
from api.models import Client
from api.serializers.client import ClientSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q

class ClientViewSet(AgencyModelViewSet):
    """
    🤝 MÜŞTERİ YÖNETİMİ (CRM)
    
    Features:
    - Müşteri veritabanı
    - Proje geçmişi
    - İletişim bilgileri
    - Segmentasyon (tags)
    - Müşteri notları
    """
    queryset = Client.objects.all().prefetch_related('projects')
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'contact_person', 'email', 'phone']
    filterset_fields = ['tags']
    ordering_fields = ['company_name', 'created_at']

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """
        📂 Müşterinin Tüm Projeleri
        Geçmiş iş birliği geçmişi
        """
        client = self.get_object()
        projects = client.projects.all().order_by('-created_at')
        
        from api.serializers.project import ProjectSerializer
        serializer = ProjectSerializer(projects, many=True)
        
        # Stats
        stats = {
            'total_projects': projects.count(),
            'completed': projects.filter(status='completed').count(),
            'in_progress': projects.filter(status='in_progress').count(),
            'planned': projects.filter(status='planned').count(),
        }
        
        # Total budget
        total_budget = projects.aggregate(
            total=Sum('budget_actual')
        )['total'] or 0
        
        return Response({
            'client': {
                'id': client.id,
                'company_name': client.company_name,
                'contact_person': client.contact_person
            },
            'stats': {
                **stats,
                'total_revenue': float(total_budget)
            },
            'projects': serializer.data
        })

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        📝 Müşteri Notu Ekle
        CRM notları (görüşmeler, özel talepler, vs.)
        """
        client = self.get_object()
        note = request.data.get('note', '').strip()
        
        if not note:
            return Response({'error': 'Not boş olamaz'}, status=400)
        
        # Mevcut notların üzerine ekle (timestamp ile)
        from django.utils import timezone
        timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
        new_note = f"[{timestamp}] {request.user.get_full_name()}: {note}"
        
        if client.notes:
            client.notes = f"{new_note}\n\n{client.notes}"
        else:
            client.notes = new_note
        
        client.save()
        
        return Response({
            'message': 'Not eklendi',
            'notes': client.notes
        })

    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """
        🏷️ Tag Ekle
        Segmentasyon için (VIP, Kurumsal, Startup, vs.)
        """
        client = self.get_object()
        tag = request.data.get('tag', '').strip()
        
        if not tag:
            return Response({'error': 'Tag boş olamaz'}, status=400)
        
        if not client.tags:
            client.tags = []
        
        if tag not in client.tags:
            client.tags.append(tag)
            client.save()
            return Response({
                'message': 'Tag eklendi',
                'tags': client.tags
            })
        else:
            return Response({
                'message': 'Tag zaten mevcut',
                'tags': client.tags
            })

    @action(detail=True, methods=['post'])
    def remove_tag(self, request, pk=None):
        """🏷️ Tag Çıkar"""
        client = self.get_object()
        tag = request.data.get('tag')
        
        if client.tags and tag in client.tags:
            client.tags.remove(tag)
            client.save()
            return Response({
                'message': 'Tag çıkarıldı',
                'tags': client.tags
            })
        else:
            return Response({'error': 'Tag bulunamadı'}, status=404)

    @action(detail=False, methods=['get'])
    def top_clients(self, request):
        """
        ⭐ En Değerli Müşteriler
        En çok proje yapılan veya en yüksek revenue'lü
        """
        # Proje sayısına göre
        top_by_projects = self.get_queryset().annotate(
            project_count=Count('projects')
        ).filter(project_count__gt=0).order_by('-project_count')[:10]
        
        result = []
        for client in top_by_projects:
            total_revenue = client.projects.aggregate(
                total=Sum('budget_actual')
            )['total'] or 0
            
            result.append({
                'id': client.id,
                'company_name': client.company_name,
                'project_count': client.projects.count(),
                'total_revenue': float(total_revenue),
                'tags': client.tags or []
            })
        
        return Response({
            'top_clients': result
        })

    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """
        🏷️ Tag'e Göre Müşteriler
        ?tag=VIP
        """
        tag = request.query_params.get('tag')
        if not tag:
            return Response({'error': 'tag parametresi gerekli'}, status=400)
        
        # JSONField içinde arama
        clients = self.get_queryset().filter(
            tags__contains=[tag]
        )
        
        serializer = self.get_serializer(clients, many=True)
        return Response({
            'tag': tag,
            'count': clients.count(),
            'clients': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        📊 Müşteri İstatistikleri (Agency-wide)
        """
        total_clients = self.get_queryset().count()
        
        # Active clients (son 6 ayda proje yaptırmış)
        from datetime import timedelta
        from django.utils import timezone
        six_months_ago = timezone.now() - timedelta(days=180)
        
        active_clients = self.get_queryset().filter(
            projects__created_at__gte=six_months_ago
        ).distinct().count()
        
        # Tag breakdown
        all_tags = []
        for client in self.get_queryset():
            if client.tags:
                all_tags.extend(client.tags)
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        
        return Response({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'tag_distribution': dict(tag_counts.most_common(10))
        })
