from api.views.base import AgencyModelViewSet
from api.models import Equipment, EquipmentCategory, EquipmentReservation
from api.serializers.equipment import EquipmentSerializer, CategorySerializer, EquipmentReservationSerializer
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from datetime import datetime

from api.permissions import HasAgencyPermission
from rest_framework.permissions import IsAuthenticated

class EquipmentViewSet(AgencyModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, HasAgencyPermission]
    required_role_permission = 'can_manage_equipment'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'scan_qr', 'check_availability']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasAgencyPermission()]
    
    search_fields = ['name', 'serial_number', 'brand', 'model']
    filterset_fields = ['category', 'status']

    @action(detail=False, methods=['post'])
    def scan_qr(self, request):
        """
        🎯 SENARYO 1: QR Kod ile Ekipman Bulma
        Mobil'den QR okutunca direkt ekipman detayını ve rezervasyon yapma imkanını veriyor
        """
        qr_code = request.data.get('qr_code')
        if not qr_code:
            return Response({'error': 'QR code gerekli'}, status=400)
        
        try:
            equipment = Equipment.objects.get(
                qr_code=qr_code,
                agency=request.user.current_agency
            )
            serializer = self.get_serializer(equipment)
            
            # Ekstra bilgi: Şu an kimde, müsait mi?
            extra_info = {
                'is_available': equipment.status == 'available',
                'current_holder': equipment.current_holder.email if equipment.current_holder else None,
                'can_reserve': True  # İleride rol bazlı kontrol eklenebilir
            }
            
            return Response({
                'equipment': serializer.data,
                'availability': extra_info
            })
        except Equipment.DoesNotExist:
            return Response({'error': 'Ekipman bulunamadı veya bu ajansa ait değil'}, status=404)

    @action(detail=True, methods=['post'])
    def check_availability(self, request, pk=None):
        """
        🎯 SENARYO 2: Müsaitlik Kontrolü + Çakışma Uyarısı
        Tarih aralığı verince, ekipman müsait mi / değilse ne zaman boşalır
        """
        equipment = self.get_object()
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date ve end_date gerekli'}, status=400)
        
        # Parse dates
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except:
            return Response({'error': 'Geçersiz tarih formatı (ISO 8601 kullanın)'}, status=400)
        
        # Çakışma kontrolü
        conflicts = EquipmentReservation.objects.filter(
            equipment=equipment,
            agency=request.user.current_agency,
            status__in=['approved', 'active']
        ).filter(
            Q(start_date__lt=end) & Q(end_date__gt=start)
        )
        
        if conflicts.exists():
            conflict_details = []
            for c in conflicts:
                conflict_details.append({
                    'project': str(c.project) if c.project else 'Bireysel Rezervasyon',
                    'reserved_by': c.reserved_by.get_full_name() or c.reserved_by.email,
                    'start_date': c.start_date,
                    'end_date': c.end_date,
                    'status': c.get_status_display()
                })
            
            return Response({
                'available': False,
                'conflicts': conflict_details,
                'can_waitlist': True,
                'message': 'Bu tarihlerde ekipman dolu. Waitlist\'e eklenebilir.'
            })
        else:
            return Response({
                'available': True,
                'message': 'Ekipman bu tarihlerde müsait!',
                'equipment_name': equipment.name
            })


class ReservationViewSet(AgencyModelViewSet):
    queryset = EquipmentReservation.objects.all().select_related(
        'equipment', 'project', 'reserved_by'
    ).order_by('start_date')
    serializer_class = EquipmentReservationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'equipment', 'project', 'reserved_by']
    
    def perform_create(self, serializer):
        serializer.save(
            agency=self.request.user.current_agency,
            reserved_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """✅ Yönetici Onayı"""
        reservation = self.get_object()
        
        if reservation.status != 'pending':
            return Response({'error': 'Sadece beklemedeki rezervasyonlar onaylanabilir'}, status=400)
        
        reservation.status = 'approved'
        reservation.save()
        
        # Email gönder (Celery async)
        from api.tasks import send_reservation_approval_email
        send_reservation_approval_email.delay(reservation.id)
        
        # Notification
        from api.services.notification import NotificationService
        NotificationService.notify_reservation_approved(reservation)
        
        return Response({
            'status': 'approved',
            'message': f'{reservation.reserved_by.get_full_name()} kullanıcısına bildirim gönderildi'
        })

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        📤 EKİPMANI TESLİM ALMA (Check-out)
        1. Rezervasyon -> Active
        2. Ekipman -> In Use
        3. Şu an kimde? -> Request User
        """
        reservation = self.get_object()
        
        # Validasyon
        if reservation.status != 'approved':
            return Response({'error': 'Sadece onaylı rezervasyonlar teslim alınabilir'}, status=400)
        
        # Tarih kontrolü: Çok erken mi?
        now = timezone.now()
        if now < reservation.start_date:
            return Response({
                'error': 'Rezervasyon tarihi henüz gelmedi',
                'start_date': reservation.start_date
            }, status=400)
        
        reservation.status = 'active'
        reservation.save()
        
        # Ekipman durumunu güncelle
        equip = reservation.equipment
        equip.status = 'in_use'
        equip.current_holder = request.user
        equip.save()
        
        return Response({
            'status': 'checked_out',
            'equipment_status': 'in_use',
            'holder': request.user.get_full_name(),
            'message': f'{equip.name} teslim alındı'
        })

    @action(detail=True, methods=['post'])
    def return_item(self, request, pk=None):
        """
        📥 EKİPMANI İADE ETME (Check-in/Return)
        1. Rezervasyon -> Completed
        2. Ekipman -> Available
        3. Durum kontrolü yapılabilir (hasarlı mı?)
        """
        reservation = self.get_object()
        
        if reservation.status != 'active':
            return Response({'error': 'Sadece aktif rezervasyonlar iade edilebilir'}, status=400)
        
        # Opsiyonel: Durum raporu
        condition = request.data.get('condition', 'good')  # good, damaged, needs_maintenance
        condition_notes = request.data.get('condition_notes', '')
        
        reservation.status = 'completed'
        reservation.notes += f"\n[İade] Durum: {condition}. Not: {condition_notes}"
        reservation.save()
        
        equip = reservation.equipment
        
        # Hasarlıysa bakıma gönder
        if condition == 'damaged' or condition == 'needs_maintenance':
            equip.status = 'maintenance'
            equip.notes += f"\n[Oto-Bakım] {timezone.now()}: {condition_notes}"
        else:
            equip.status = 'available'
        
        equip.current_holder = None
        equip.save()
        
        # TODO: Waitlist varsa ilk sıradakine bildirim gönder
        
        return Response({
            'status': 'returned',
            'equipment_status': equip.status,
            'message': f'{equip.name} başarıyla iade edildi'
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """❌ Rezervasyon İptali"""
        reservation = self.get_object()
        
        if reservation.status in ['completed', 'cancelled']:
            return Response({'error': 'Bu rezervasyon zaten tamamlanmış veya iptal edilmiş'}, status=400)
        
        # Eğer aktifse (teslim alınmışsa), ekipmanı da geri al
        if reservation.status == 'active':
            equip = reservation.equipment
            equip.status = 'available'
            equip.current_holder = None
            equip.save()
        
        reservation.status = 'cancelled'
        reservation.save()
        
        # TODO: Waitlist'ten sonraki kişiye bildirim
        
        return Response({'status': 'cancelled', 'message': 'Rezervasyon iptal edildi'})


class CategoryViewSet(AgencyModelViewSet):
    queryset = EquipmentCategory.objects.all()
    serializer_class = CategorySerializer
