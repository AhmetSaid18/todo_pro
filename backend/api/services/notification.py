"""
🔔 Notification Service
Bildirim gönderme helper fonksiyonları
Celery ile async olarak çalıştırılabilir
"""
from api.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationService:
    
    @staticmethod
    def send(user, agency, notification_type, title, message, link=None):
        """
        Kullanıcıya bildirim gönder
        
        Args:
            user: User instance
            agency: Agency instance  
            notification_type: 'info', 'success', 'warning', 'error'
            title: Bildirim başlığı
            message: Bildirim mesajı
            link: Opsiyonel link (frontend route)
        """
        # Database'e kaydet
        notification = Notification.objects.create(
            user=user,
            agency=agency,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
        
        # WebSocket ile real-time gönder (Django Channels)
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user.id}',
                {
                    'type': 'notification_message',
                    'notification': {
                        'id': notification.id,
                        'type': notification_type,
                        'title': title,
                        'message': message,
                        'link': link,
                        'created_at': notification.created_at.isoformat()
                    }
                }
            )
        except Exception as e:
            # Eğer WebSocket başarısız olursa, en azından DB'de var
            print(f"WebSocket notification failed: {e}")
        
        return notification

    @staticmethod
    def notify_reservation_approved(reservation):
        """Rezervasyon onaylandı bildirimi"""
        return NotificationService.send(
            user=reservation.reserved_by,
            agency=reservation.agency,
            notification_type='success',
            title='Rezervasyon Onaylandı',
            message=f'{reservation.equipment.name} rezervasyonunuz onaylandı. {reservation.start_date.strftime("%d/%m/%Y")} tarihinde teslim alabilirsiniz.',
            link=f'/reservations/{reservation.id}'
        )

    @staticmethod
    def notify_task_revision(task):
        """Görev revizyon gerekiyor bildirimi"""
        return NotificationService.send(
            user=task.assigned_to,
            agency=task.agency,
            notification_type='warning',
            title='Revizyon Gerekiyor',
            message=f'"{task.title}" göreviniz için revizyon istendi.',
            link=f'/tasks/{task.id}'
        )

    @staticmethod
    def notify_task_approved(task):
        """Görev onaylandı bildirimi"""
        return NotificationService.send(
            user=task.assigned_to,
            agency=task.agency,
            notification_type='success',
            title='Görev Onaylandı! 🎉',
            message=f'"{task.title}" göreviniz başarıyla tamamlandı.',
            link=f'/tasks/{task.id}'
        )

    @staticmethod
    def notify_equipment_available(user, agency, equipment):
        """Waitlist: Ekipman boşa çıktı bildirimi"""
        return NotificationService.send(
            user=user,
            agency=agency,
            notification_type='info',
            title='Ekipman Müsait! ⚡',
            message=f'{equipment.name} boşa çıktı! Hemen rezerve edebilirsiniz.',
            link=f'/equipment/{equipment.id}'
        )
