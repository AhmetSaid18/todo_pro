from api.views.base import AgencyModelViewSet
from api.models import Location
from api.serializers.location import LocationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

class LocationViewSet(AgencyModelViewSet):
    """
    📍 LOKASYON YÖNETİMİ
    
    Features:
    - Lokasyon kütüphanesi
    - Detaylar (adres, izinler, notlar)
    - Fotoğraflar
    - Müsaitlik
    - Maliyet bilgileri
    - Favoriler
    """
    queryset = Location.objects.all().prefetch_related('projects')
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'description']
    filterset_fields = ['is_favorite', 'requires_permit']
    ordering_fields = ['name', 'created_at', 'usage_count']

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk=None):
        """⭐ Favorilere Ekle"""
        location = self.get_object()
        location.is_favorite = True
        location.save()
        
        return Response({
            'status': 'added_to_favorites',
            'message': f'{location.name} favorilere eklendi'
        })

    @action(detail=True, methods=['post'])
    def remove_from_favorites(self, request, pk=None):
        """⭐ Favorilerden Çıkar"""
        location = self.get_object()
        location.is_favorite = False
        location.save()
        
        return Response({
            'status': 'removed_from_favorites',
            'message': f'{location.name} favorilerden çıkarıldı'
        })

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """⭐ Favori Lokasyonlar"""
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        
        return Response({
            'count': favorites.count(),
            'favorites': serializer.data
        })

    @action(detail=True, methods=['get'])
    def usage_history(self, request, pk=None):
        """
        📊 Kullanım Geçmişi
        Bu lokasyonda yapılan projeler
        """
        location = self.get_object()
        projects = location.projects.all().order_by('-created_at')
        
        from api.serializers.project import ProjectSerializer
        serializer = ProjectSerializer(projects, many=True)
        
        return Response({
            'location': {
                'id': location.id,
                'name': location.name,
                'address': location.address
            },
            'usage_count': projects.count(),
            'projects': serializer.data
        })

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        📝 Not Ekle
        Praktikal bilgiler (park yeri, elektrik, vs.)
        """
        location = self.get_object()
        note = request.data.get('note', '').strip()
        
        if not note:
            return Response({'error': 'Not boş olamaz'}, status=400)
        
        from django.utils import timezone
        timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
        new_note = f"[{timestamp}] {request.user.get_full_name()}: {note}"
        
        if location.notes:
            location.notes = f"{new_note}\n\n{location.notes}"
        else:
            location.notes = new_note
        
        location.save()
        
        return Response({
            'message': 'Not eklendi',
            'notes': location.notes
        })

    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """
        📸 Fotoğraf Ekle
        Lokasyon fotoğrafları
        """
        location = self.get_object()
        photo_url = request.data.get('photo_url')
        
        if not photo_url:
            return Response({'error': 'photo_url gerekli'}, status=400)
        
        if not location.photos:
            location.photos = []
        
        location.photos.append({
            'url': photo_url,
            'uploaded_by': request.user.get_full_name(),
            'uploaded_at': timezone.now().isoformat()
        })
        location.save()
        
        return Response({
            'message': 'Fotoğraf eklendi',
            'total_photos': len(location.photos)
        })

    @action(detail=False, methods=['get'])
    def requires_permit(self, request):
        """
        📋 İzin Gereken Lokasyonlar
        Permit tracking
        """
        locations = self.get_queryset().filter(requires_permit=True)
        serializer = self.get_serializer(locations, many=True)
        
        return Response({
            'count': locations.count(),
            'locations': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        📊 Lokasyon İstatistikleri
        """
        total = self.get_queryset().count()
        favorites = self.get_queryset().filter(is_favorite=True).count()
        requires_permit = self.get_queryset().filter(requires_permit=True).count()
        
        # En çok kullanılan lokasyonlar
        most_used = self.get_queryset().annotate(
            project_count=Count('projects')
        ).filter(project_count__gt=0).order_by('-project_count')[:5]
        
        return Response({
            'total_locations': total,
            'favorites': favorites,
            'requires_permit': requires_permit,
            'most_used': [
                {
                    'id': loc.id,
                    'name': loc.name,
                    'usage_count': loc.projects.count()
                }
                for loc in most_used
            ]
        })

    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """
        ✅ Müsaitlik Kontrolü
        ?start_date=2026-01-20&end_date=2026-01-25
        """
        location = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date ve end_date gerekli'}, status=400)
        
        from datetime import datetime
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            return Response({'error': 'Geçersiz tarih formatı'}, status=400)
        
        # Bu tarihler arasında bu lokasyonda proje var mı?
        conflicting_projects = location.projects.filter(
            Q(start_date__lt=end) & Q(end_date__gt=start),
            status__in=['planned', 'in_progress']
        )
        
        if conflicting_projects.exists():
            conflicts = [
                {
                    'project': p.title,
                    'start_date': p.start_date,
                    'end_date': p.end_date
                }
                for p in conflicting_projects
            ]
            
            return Response({
                'available': False,
                'conflicts': conflicts,
                'message': 'Bu tarihlerde lokasyon dolu'
            })
        else:
            return Response({
                'available': True,
                'message': 'Lokasyon bu tarihlerde müsait'
            })
