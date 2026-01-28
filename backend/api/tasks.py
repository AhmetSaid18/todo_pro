"""
🔥 CELERY TASKS
Async işlemler: Email, Notifications, Scheduled Jobs
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from api.models import Task, ShootingDay, EquipmentReservation, Notification, User

@shared_task
def send_email_notification(subject, message, recipient_list):
    """
    📧 Email Gönder
    Async email gönderme
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f"Email sent to {len(recipient_list)} recipients"
    except Exception as e:
        return f"Email failed: {str(e)}"


@shared_task
def send_task_assignment_email(task_id):
    """
    📋 Görev Atama Maili
    Kullanıcıya yeni görev atandığında
    """
    try:
        task = Task.objects.select_related('assigned_to', 'project').get(id=task_id)
        
        if not task.assigned_to or not task.assigned_to.email:
            return "No email recipient"
        
        subject = f'Yeni Görev: {task.title}'
        message = f"""
Merhaba {task.assigned_to.get_full_name()},

Size yeni bir görev atandı:

Görev: {task.title}
Proje: {task.project.title if task.project else 'Bağımsız'}
Öncelik: {task.get_priority_display()}
Bitiş Tarihi: {task.due_date.strftime('%d/%m/%Y %H:%M') if task.due_date else 'Belirtilmemiş'}

Açıklama:
{task.description}

Görevi görmek için: {settings.FRONTEND_URL}/tasks/{task.id}

İyi çalışmalar!
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=False,
        )
        
        return f"Task assignment email sent to {task.assigned_to.email}"
    
    except Task.DoesNotExist:
        return "Task not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_shooting_reminder_emails():
    """
    🎬 Yarınki Çekim Hatırlatması
    Her gün akşam çalışır, yarın çekimi olan herkese mail atar
    
    Celery Beat ile scheduled: Her gün 18:00'da
    """
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Yarın çekimi olan günler
    shooting_days = ShootingDay.objects.filter(
        shoot_date=tomorrow,
        status__in=['planned', 'confirmed']
    ).select_related('project')
    
    if not shooting_days.exists():
        return "No shootings tomorrow"
    
    emails_sent = 0
    
    for shooting_day in shooting_days:
        # Projedeki tüm ekip üyeleri
        if shooting_day.project:
            team_members = shooting_day.project.team_members.all()
            
            for member in team_members:
                if not member.email:
                    continue
                
                subject = f'Yarın Çekiminiz Var: {shooting_day.project.title}'
                message = f"""
Merhaba {member.get_full_name()},

Yarın çekiminiz var:

Proje: {shooting_day.project.title}
Tarih: {tomorrow.strftime('%d/%m/%Y')}
Saat: {shooting_day.call_time.strftime('%H:%M') if shooting_day.call_time else 'Belirtilmemiş'}
Lokasyon: {shooting_day.location or 'Belirtilmemiş'}

Ekip: {shooting_day.crew_size or 'Belirtilmemiş'} kişi

Notlar:
{shooting_day.notes or 'Yok'}

Çekim detayları: {settings.FRONTEND_URL}/shooting-days/{shooting_day.id}

Hazırlıklı olun!
"""
                
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[member.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
                except:
                    pass
    
    return f"Shooting reminders sent: {emails_sent} emails"


@shared_task
def send_reservation_approval_email(reservation_id):
    """
    ✅ Rezervasyon Onaylandı Maili
    """
    try:
        reservation = EquipmentReservation.objects.select_related(
            'equipment', 'reserved_by', 'project'
        ).get(id=reservation_id)
        
        if not reservation.reserved_by.email:
            return "No email"
        
        subject = f'Rezervasyon Onaylandı: {reservation.equipment.name}'
        message = f"""
Merhaba {reservation.reserved_by.get_full_name()},

Ekipman rezervasyonunuz onaylandı!

Ekipman: {reservation.equipment.name}
Tarih: {reservation.start_date.strftime('%d/%m/%Y')} - {reservation.end_date.strftime('%d/%m/%Y')}
Proje: {reservation.project.title if reservation.project else 'Bireysel'}

Ekipmanı {reservation.start_date.strftime('%d/%m/%Y')} tarihinde teslim alabilirsiniz.

Rezervasyon detayı: {settings.FRONTEND_URL}/reservations/{reservation.id}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.reserved_by.email],
            fail_silently=False,
        )
        
        return f"Reservation approval email sent"
    
    except EquipmentReservation.DoesNotExist:
        return "Reservation not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_task_revision_email(task_id):
    """
    🔄 Revizyon Gerekiyor Maili
    """
    try:
        task = Task.objects.select_related('assigned_to', 'project').get(id=task_id)
        
        if not task.assigned_to or not task.assigned_to.email:
            return "No email"
        
        subject = f'Revizyon Gerekiyor: {task.title}'
        message = f"""
Merhaba {task.assigned_to.get_full_name()},

"{task.title}" görevi için revizyon talep edildi.

Revizyon Notları:
{task.revision_notes or 'Belirtilmemiş'}

Lütfen gerekli düzeltmeleri yapıp tekrar gönderin.

Görev detayı: {settings.FRONTEND_URL}/tasks/{task.id}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=False,
        )
        
        return f"Revision email sent"
    
    except Task.DoesNotExist:
        return "Task not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_task_approved_email(task_id):
    """
    ✅ Görev Onaylandı Maili
    """
    try:
        task = Task.objects.select_related('assigned_to').get(id=task_id)
        
        if not task.assigned_to or not task.assigned_to.email:
            return "No email"
        
        subject = f'Görev Onaylandı: {task.title} 🎉'
        message = f"""
Tebrikler {task.assigned_to.get_full_name()}!

"{task.title}" göreviniz onaylandı ve başarıyla tamamlandı!

Harika iş çıkardınız! 🎉

Görev detayı: {settings.FRONTEND_URL}/tasks/{task.id}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=False,
        )
        
        return f"Approval email sent"
    
    except Task.DoesNotExist:
        return "Task not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def check_overdue_tasks():
    """
    ⏰ Geciken Görevleri Kontrol Et
    Süresi geçmiş görevler için bildirim gönder
    
    Celery Beat ile scheduled: Her gün 09:00'da
    """
    now = timezone.now()
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['not_started', 'in_progress']
    ).select_related('assigned_to')
    
    notifications_sent = 0
    
    for task in overdue_tasks:
        if task.assigned_to:
            # Notification oluştur
            Notification.objects.create(
                user=task.assigned_to,
                agency=task.agency,
                notification_type='warning',
                title='Görev Gecikti!',
                message=f'"{task.title}" göreviniz {(now - task.due_date).days} gün gecikmiş durumda.',
                link=f'/tasks/{task.id}'
            )
            notifications_sent += 1
    
    return f"Overdue notifications sent: {notifications_sent}"


@shared_task
def check_equipment_late_returns():
    """
    📦 Geç Teslim Edilen Ekipmanları Kontrol Et
    
    Celery Beat ile scheduled: Her gün 2 kez (10:00, 16:00)
    """
    now = timezone.now()
    
    # Süresi geçmiş aktif rezervasyonlar
    late_reservations = EquipmentReservation.objects.filter(
        end_date__lt=now,
        status='active'
    ).select_related('reserved_by', 'equipment')
    
    notifications_sent = 0
    
    for reservation in late_reservations:
        if reservation.reserved_by:
            days_late = (now - reservation.end_date).days
            
            Notification.objects.create(
                user=reservation.reserved_by,
                agency=reservation.agency,
                notification_type='error',
                title='Ekipman Teslimi Gecikti!',
                message=f'{reservation.equipment.name} ekipmanı {days_late} gün gecikmiş. Lütfen acilen iade edin.',
                link=f'/reservations/{reservation.id}'
            )
            
            # Email de gönder
            if reservation.reserved_by.email:
                send_mail(
                    subject='Ekipman Teslimi Gecikti!',
                    message=f"""
Merhaba {reservation.reserved_by.get_full_name()},

{reservation.equipment.name} ekipmanını {days_late} gündür iade etmediniz.

İade tarihi: {reservation.end_date.strftime('%d/%m/%Y')}
Bugün: {now.strftime('%d/%m/%Y')}

Lütfen ekipmanı acilen iade edin.
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reservation.reserved_by.email],
                    fail_silently=True,
                )
            
            notifications_sent += 1
    
    return f"Late return warnings sent: {notifications_sent}"


@shared_task
def daily_digest_email():
    """
    📊 Günlük Özet Maili
    Yöneticilere günlük durum raporu
    
    Celery Beat ile scheduled: Her gün 08:00'da
    """
    from api.models import Agency, AgencyMembership
    
    emails_sent = 0
    
    # Tüm agency'leri döngüye al
    for agency in Agency.objects.filter(is_active=True):
        # Owner'ları bul
        owners = User.objects.filter(
            memberships__agency=agency,
            memberships__is_owner=True,
            memberships__is_active=True
        )
        
        # İstatistikler
        today = timezone.now().date()
        
        tasks_today = Task.objects.filter(
            agency=agency,
            due_date__date=today
        ).count()
        
        shootings_today = ShootingDay.objects.filter(
            agency=agency,
            shoot_date=today
        ).count()
        
        pending_approvals = Task.objects.filter(
            agency=agency,
            status='in_review'
        ).count()
        
        # Owner'lara mail gönder
        for owner in owners:
            if not owner.email:
                continue
            
            subject = f'Günlük Özet - {agency.name}'
            message = f"""
Merhaba {owner.get_full_name()},

Bugün için özet:

📋 Bugün Bitmesi Gereken Görevler: {tasks_today}
🎬 Bugünkü Çekimler: {shootings_today}
⏳ Onay Bekleyen Görevler: {pending_approvals}

Detaylar için: {settings.FRONTEND_URL}/dashboard

İyi çalışmalar!
"""
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[owner.email],
                    fail_silently=True,
                )
                emails_sent += 1
            except:
                pass
    
    return f"Daily digest emails sent: {emails_sent}"
