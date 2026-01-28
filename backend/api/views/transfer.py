from api.views.base import AgencyModelViewSet
from api.models import FileTransfer
from api.serializers.transfer import FileTransferSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import uuid

class TransferViewSet(AgencyModelViewSet):
    """
    📤 WE-TRANSFER MODULE
    
    Sinematik dosyaların dışarıya (müşteriye) güvenli transferi.
    """
    queryset = FileTransfer.objects.all().select_related('project', 'created_by')
    serializer_class = FileTransferSerializer

    def perform_create(self, serializer):
        # Create unique link
        unique_id = uuid.uuid4().hex[:12]
        # Example URL: https://yoursite.com/t/unique_id
        download_link = f"/t/{unique_id}"
        
        serializer.save(
            agency=self.request.user.current_agency,
            created_by=self.request.user,
            download_link=download_link,
            expires_at=timezone.now() + timezone.timedelta(days=7) # Default 7 days
        )

    @action(detail=True, methods=['post'])
    def extend_expiry(self, request, pk=None):
        """Süreyi 7 gün daha uzatır."""
        transfer = self.get_object()
        transfer.expires_at += timezone.timedelta(days=7)
        transfer.save()
        return Response({'status': 'extended', 'expires_at': transfer.expires_at})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Transfer istatistiklerini getirir."""
        total_transfers = self.get_queryset().count()
        active_transfers = self.get_queryset().filter(status='active').count()
        return Response({
            'total_transfers': total_transfers,
            'active_transfers': active_transfers
        })
