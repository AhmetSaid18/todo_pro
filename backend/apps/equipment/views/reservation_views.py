from apps.core.views import AgencyModelViewSet
from apps.equipment.models import EquipmentReservation
from apps.equipment.serializers import EquipmentReservationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ReservationViewSet(AgencyModelViewSet):
    queryset = EquipmentReservation.objects.all().order_by('start_date')
    serializer_class = EquipmentReservationSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            agency=self.request.user.current_agency,
            reserved_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'approved'
        reservation.save()
        return Response({'status': 'approved'})
