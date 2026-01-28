from apps.core.views import AgencyModelViewSet
from apps.equipment.models import Equipment
from apps.equipment.serializers import EquipmentSerializer
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

class EquipmentViewSet(AgencyModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'serial_number', 'brand']
    filterset_fields = ['category', 'status']

    @action(detail=False, methods=['get'])
    def scan_qr(self, request):
        """
        QR Kodu okutup ekipmanı bulur.
        GET /api/equipment/items/scan_qr/?code=XYZ
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Code parameter required'}, status=400)
        
        try:
            # Sadece kendi ajansında ara
            equipment = self.get_queryset().get(qr_code=code)
            serializer = self.get_serializer(equipment)
            return Response(serializer.data)
        except Equipment.DoesNotExist:
            return Response({'error': 'Ekipman bulunamadı veya yetkiniz yok.'}, status=404)
