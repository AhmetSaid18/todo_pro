# 🔥 CELERY TASKS TAMAMLANDI!

## ✅ CELERY TASK SİSTEMİ

### 📧 Email Tasks (Async)

#### 1. `send_task_assignment_email(task_id)`
- **Ne zaman:** Yeni görev atandığında
- **Kime:** Görevi atanan kişiye
- **İçerik:** Görev detayları, deadline, link

#### 2. `send_task_approved_email(task_id)`
- **Ne zaman:** Görev onaylandığında
- **Kime:** Görevi tamamlayan kişiye
- **İçerik:** Tebrik mesajı 🎉

#### 3. `send_task_revision_email(task_id)`
- **Ne zaman:** Revizyon istendiğinde
- **Kime:** Görevi yapan kişiye
- **İçerik:** Revizyon notları

#### 4. `send_reservation_approval_email(reservation_id)`
- **Ne zaman:** Rezervasyon onaylandığında
- **Kime:** Rezervasyonu yapan kişiye
- **İçerik:** Ekipman, tarih, teslim alma bilgisi

---

### ⏰ Scheduled Tasks (Celery Beat)

#### 1. `send_shooting_reminder_emails` - HER GÜN 18:00 ✅
- **Ne yapar:** Yarın çekimi olan herkese hatırlatma maili atar
- **Detay:**
  - Proje adı
  - Tarih, saat
  - Lokasyon
  - Ekip bilgisi
  - Link

#### 2. `check_overdue_tasks` - HER GÜN 09:00
- **Ne yapar:** Süresi geçmiş görevleri bulur, notification gönderir
- **Kime:** Görev sahibi

#### 3. `check_equipment_late_returns` - HER GÜN 10:00 ve 16:00
- **Ne yapar:** İade edilmemiş ekipmanlar için uyarı
- **Tetikler:** 
  - Notification
  - Email (geç iade uyarısı)

#### 4. `daily_digest_email` - HER GÜN 08:00
- **Ne yapar:** Günlük özet raporu
- **Kime:** Agency owner'ları
- **İçerik:**
  - Bugün bitmesi gereken görevler
  - Bugünkü çekimler
  - Onay bekleyen görevler

---

## 🏗️ Celery Beat Schedule

```python
{
    'shooting-reminder-daily': {
        'schedule': crontab(hour=18, minute=0),  # 18:00
    },
    'check-overdue-tasks-daily': {
        'schedule': crontab(hour=9, minute=0),  # 09:00
    },
    'check-late-returns-twice-daily': {
        'schedule': crontab(hour='10,16', minute=0),  # 10:00, 16:00
    },
    'daily-digest-email': {
        'schedule': crontab(hour=8, minute=0),  # 08:00
    },
}
```

---

## 🎯 Kullanım

### Async Task Çağırma (View'lardan):
```python
from api.tasks import send_task_approved_email

# Async olarak çalıştır
send_task_approved_email.delay(task.id)
```

### Notification + Email Birlikte:
```python
# 1. Notification (DB + WebSocket)
from api.services.notification import NotificationService
NotificationService.notify_task_approved(task)

# 2. Email (Celery async)
from api.tasks import send_task_approved_email
send_task_approved_email.delay(task.id)
```

---

## ✅ View'lara Entegre Edildi:

1. **TaskViewSet**
   - `approve()` → Email + Notification ✅
   - `request_revision()` → Email + Notification ✅

2. **ReservationViewSet**
   - `approve()` → Email + Notification ✅

---

## 🚀 Production'da Çalıştırma:

### 1. Celery Worker:
```bash
docker-compose up celery
# veya manuel:
celery -A config worker -l info
```

### 2. Celery Beat (Scheduler):
```bash
docker-compose up celery-beat
# veya manuel:
celery -A config beat -l info
```

### 3. İkisi Birlikte:
```bash
docker-compose up web celery celery-beat
```

---

## 📧 Email Ayarları

### Development (Console):
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Email'ler console'a yazılır, gerçek mail gitmez.

### Production (SMTP):
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🎯 Task Özeti:

| Task | Trigger | Frequency | Recipient |
|------|---------|-----------|-----------|
| Shooting Reminder | Scheduled | Her gün 18:00 | Yarın çekimi olanlar |
| Overdue Tasks | Scheduled | Her gün 09:00 | Geciken görev sahipleri |
| Late Returns | Scheduled | 10:00, 16:00 | Geç iade edenler |
| Daily Digest | Scheduled | Her gün 08:00 | Owner'lar |
| Task Approval | On-demand | - | Görev sahibi |
| Task Revision | On-demand | - | Görev sahibi |
| Reservation Approval | On-demand | - | Rezervasyon sahibi |

---

## ✅ TAMAMLANDI!

- ✅ Celery tasks implemented
- ✅ Email system ready
- ✅ Scheduled tasks configured
- ✅ Beat schedule active
- ✅ View integration done
- ✅ Notification + Email combo

**HER ŞEY HAZIR AGA! 🔥**

---

**Date:** 2026-01-18  
**Status:** COMPLETE ✅  
**Team:** Fatih Abi + Antigravity 🚀
