# 📚 Todo Production API Documentation

**Base URL:** `/api/v1/`
**Auth Header:** `Authorization: Bearer <your_access_token>`

Bu doküman projedeki tüm endpoint'leri, request örneklerini ve kuralları içerir.
Her yeni özellik geliştirmesinde bu dosya **GÜNCELLENMELİDİR**.

---

## 🔐 1. Users

*(Login/Register endpoint'leri henüz eklenmedi, Django Admin üzerinden yönetiliyor)*

---

## 🎬 2. Projects (Projeler)

### `GET /projects/`
Ajansa ait tüm projeleri listeler.
- **Query Params:**
  - `status`: `standard_planning`, `active_production`, `completed`
  - `priority`: `low`, `medium`, `high`
  - `search`: Başlık veya müşteri isminde arama
  - `ordering`: `-updated_at` (default), `start_date`
  - `is_template`: `true` (Şablonları listele) veya `false` (Projeleri listele)

### `POST /projects/`
Yeni proje veya şablon oluşturur.
**Body:**
```json
{
  "title": "Müzik Klibi Şablonu",
  "is_template": true, 
  "tags": ["Şablon", "Klip"]
}
```

### `POST /projects/{id}/create_from_template/`
Var olan bir şablondan (veya projeden) yeni proje yaratır. Altındaki tüm görevleri (Tasks) kopyalar.
**Body:**
```json
{
  "title": "Yeni Tarkan Klibi 2026"
}
```
  "title": "X Marka Reklam Filmi",
  "client_name": "X Marka A.Ş.",
  "status": "standard_planning",
  "priority": "high",
  "start_date": "2026-05-20T09:00:00Z",
  "end_date": "2026-05-25T18:00:00Z",
  "budget_estimated": 50000.00,
  "tags": ["Reklam", "Dış Çekim"]
}
```

### `GET /projects/{id}/`
Proje detayını döner. `assigned_team` içindeki kullanıcıların tam adını ve rolünü içerir.

---

## 📝 3. Tasks (Görevler)

### `GET /tasks/`
Tüm görevleri listeler.
- **Query Params:**
  - `project`: Proje ID'si ile filtrele
  - `assigned_to`: Kullanıcı ID'si ile filtrele (Benim görevlerim)
  - `status`: `todo`, `in_progress`, `done`

### `POST /tasks/`
Projeye yeni görev ekler.
**Body:**
```json
{
  "project": "uuid-of-project",
  "title": "Set Kurulumu",
  "description": "Işıkların ayarlanması ve kameranın hazırlanması",
  "assigned_to": ["uuid-user-1", "uuid-user-2"],
  "priority": "critical",
  "due_date": "2026-05-20T08:30:00Z",
  "checklist": [
    {"item": "Bataryalar şarj edildi", "done": false},
    {"item": "Lens temizlendi", "done": true}
  ]
}
```

### `POST /tasks/{id}/toggle_status/`
Görevin durumunu `done` <-> `todo` arasında değiştirir. Hızlı aksiyon içindir.
**Body:** (Boş)

---

## 🎥 4. Equipment Inventory (Envanter)

### `GET /items/`
Envanterdeki tüm ekipmanları listeler.
- **Query Params:**
  - `category`: Kategori ID'si
  - `status`: `available`, `in_use`, `maintenance`
  - `search`: İsim, marka veya seri no araması

### `POST /items/`
Yeni ekipman ekler.
**Body:**
```json
{
  "category": "uuid-category",
  "name": "Sony A7S III",
  "brand": "Sony",
  "serial_number": "SN998877",
  "qr_code": "SONY-A7S-001",
  "status": "available"
}
```

---

## 📅 5. Reservations (Rezervasyon)

### `POST /reservations/`
Ekipman rezervasyonu yapar.
⚠️ **CRITICAL:** Sistem, girilen tarih aralığında çakışan (overlap) başka bir rezervasyon var mı diye kontrol eder. Varsa `400 Bad Request` döner.

**Body:**
```json
{
  "equipment": "uuid-equipment",
  "project": "uuid-project",
  "start_date": "2026-05-20T08:00:00Z",
  "end_date": "2026-05-25T20:00:00Z",
  "notes": "Çekim için lazım"
}
```

### `POST /reservations/{id}/approve/`
(Admin/Manager Only)
Bekleyen bir rezervasyonu onaylar (`status: approved`).

### `POST /reservations/{id}/checkout/`
**Ekipmanı Teslim Alma.**
Sadece statüsü `approved` olan rezervasyonlar için çalışır.
- Rezervasyonu `active` yapar.
- Ekipmanı `in_use` moduna alır ve `current_holder` olarak sizi kaydeder.

### `POST /reservations/{id}/return_item/`
**Ekipmanı İade Etme.**
Sadece statüsü `active` olan rezervasyonlar için çalışır.
- Rezervasyonu `completed` yapar.
- Ekipmanı `available` moduna alır ve boşa çıkarır.

---

## 📂 6. Categories (Kategoriler)

### `GET /categories/`
Ekipman kategorilerini listeler.

### `POST /categories/`
Yeni kategori ekler.
```json
{
  "name": "Kamera",
  "slug": "camera"
}
```
