from api.views.base import AgencyModelViewSet
from api.models import Notification
from api.serializers.notification import NotificationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class NotificationViewSet(AgencyModelViewSet):
    """
    🔔 Bildirimler
    Real-time notification sistemi
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Sadece kullanıcının kendi bildirimlerini göster
        return Notification.objects.filter(
            user=self.request.user,
            agency=self.request.user.current_agency
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Okunmamış bildirimler"""
        unread = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread, many=True)
        return Response({
            'count': unread.count(),
            'notifications': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Bildirimi okundu işaretle"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Tümünü okundu işaretle"""
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'marked_as_read': count})
