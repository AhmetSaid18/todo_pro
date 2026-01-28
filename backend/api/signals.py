from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from api.models import Task, Notification, EquipmentReservation, AgencyMembership

def send_realtime_notification(user_id, title, message, link):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "message": {
                "title": title,
                "message": message,
                "link": link
            }
        }
    )

@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    pass

@receiver(m2m_changed, sender=Task.assigned_to.through)
def task_assigned_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            Notification.objects.create(
                agency=instance.agency,
                user_id=user_id,
                title="Yeni Görev Atandı!",
                message=f"{instance.title} görevi size atandı.",
                notification_type='info',
                link=f"/tasks/{instance.id}"
            )
            send_realtime_notification(user_id, "Yeni Görev", f"{instance.title} size atandı.", f"/tasks/{instance.id}")

@receiver(post_save, sender=EquipmentReservation)
def reservation_notification(sender, instance, created, **kwargs):
    """
    Yeni rezervasyon talebi geldiğinde Yöneticilere bildir.
    """
    if created and instance.status == 'pending':
        # Ajansın yöneticilerini bul (Owner veya Manager)
        # Not: AgencyRole'de `can_manage_equipment` yetkisi olanları bulmak daha doğru olurdu (V2)
        managers = AgencyMembership.objects.filter(
            agency=instance.agency,
            role__can_manage_equipment=True 
        ).values_list('user_id', flat=True)
        
        # Eğer dinamik rol ile bulamazsak (henüz rol yetkileri set edilmediyse) owner'a at
        if not managers:
             managers = AgencyMembership.objects.filter(agency=instance.agency, is_owner=True).values_list('user_id', flat=True)

        for admin_id in managers:
            # Bildirimi oluşturan kişiye bildirim gitmesin (Kendisi yöneticiyse)
            if admin_id == instance.reserved_by.id:
                continue

            Notification.objects.create(
                agency=instance.agency,
                user_id=admin_id,
                title="Yeni Ekipman Talebi",
                message=f"{instance.reserved_by.first_name}, {instance.equipment.name} için rezervasyon istedi.",
                notification_type='warning',
                link=f"/equipment/requests/{instance.id}"
            )
            send_realtime_notification(admin_id, "Ekipman Talebi", f"{instance.equipment.name} istendi.", f"/requests/{instance.id}")
