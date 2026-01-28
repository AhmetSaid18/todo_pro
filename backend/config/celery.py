import os
from celery import Celery
from celery.schedules import crontab

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('todo_production')

# Ayarları settings.py'dan al (CELERY_ ile başlayanları)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Task'leri otomatik bul
app.autodiscover_tasks()

# ============================================================================
# CELERY BEAT SCHEDULE (Scheduled Tasks)
# ============================================================================
app.conf.beat_schedule = {
    # Her gün 18:00'da yarınki çekim hatırlatması
    'shooting-reminder-daily': {
        'task': 'api.tasks.send_shooting_reminder_emails',
        'schedule': crontab(hour=18, minute=0),  # Her gün 18:00
    },
    
    # Her gün 09:00'da geciken görevleri kontrol et
    'check-overdue-tasks-daily': {
        'task': 'api.tasks.check_overdue_tasks',
        'schedule': crontab(hour=9, minute=0),  # Her gün 09:00
    },
    
    # Her gün 10:00 ve 16:00'da geç teslim kontrol
    'check-late-returns-twice-daily': {
        'task': 'api.tasks.check_equipment_late_returns',
        'schedule': crontab(hour='10,16', minute=0),  # 10:00 ve 16:00
    },
    
    # Her gün 08:00'da günlük özet maili (sadece owner'lara)
    'daily-digest-email': {
        'task': 'api.tasks.daily_digest_email',
        'schedule': crontab(hour=8, minute=0),  # Her gün 08:00
    },
}

app.conf.timezone = 'Europe/Istanbul'
