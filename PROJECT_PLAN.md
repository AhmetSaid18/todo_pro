# 🎬 TODO PRODUCTION MANAGEMENT SYSTEM - Proje Planı

## 📋 Genel Bilgi

**Proje Adı:** Todo Production Management System  
**Tür:** Multi-Tenant SaaS Web Uygulaması  
**Sektör:** Sinematik Prodüksiyon & Video Çekim Yönetimi  
**Hedef:** ClickUp-style proje yönetimi + Ekipman/Depo yönetimi  
**Kullanıcılar:** Prodüksiyon firmaları (firma içi kullanım)  
**Ürün Stratejisi:** SaaS - Her firma kendi workspace'inde çalışır

---

## 🎯 İŞ AKIŞI (Workflow)

```
1. İŞ GİRİŞİ (Job/Proje)
   ├─ Müşteriden iş gelir
   ├─ Fatih (Owner/Admin) işi sisteme girer
   └─ İş detayları: Ne çekilecek, tarih, lokasyon, vs.
   
2. PLANLAMA
   ├─ Personel Atama → Kameraman, ışıkçı, ses vs.
   ├─ Ekipman Atama → Kamera, lens, ışık, vs.
   ├─ Tarih/Saat → Çekim zamanı
   └─ Lokasyon
   
3. GÖREV DAĞITIMI
   ├─ Sistem otomatik bildirim gönderir
   ├─ Çalışanlar mobil'den görür
   └─ "Görevi aldım" onayı
   
4. SÜREÇ TAKİBİ
   ├─ Çalışan: "Lokasyona gittim"
   ├─ Çalışan: "Ekipmanları aldım" (Check-out)
   ├─ Çalışan: "Çekime başladık"
   ├─ Çalışan: "Çekim tamamlandı"
   └─ Çalışan: "Ekipmanları iade ettim" (Check-in)
   
5. REVİZYON & GÖZDEN GEÇİRME
   ├─ Fatih: "Revizyon gerekiyor" → Görev geri döner
   ├─ Çalışan: Revizyonu yapar, tekrar yükler
   └─ Fatih: "Onaylandı" → İş kapanır
   
6. TAMAMLAMA
   ├─ İş tamamlandı olarak işaretlenir
   ├─ Rapor oluşur
   └─ Müşteriye teslim
```

---

## 🎬 DETAYLI SENARYOLAR (SCENARIOS)

Bu senaryolar, sistemin tasarımı ve kodlanması sırasında "Kutsal Kurallar" olarak kabul edilecektir.

### 1️⃣ SENARYO: QR Kod ile Bağımsız Rezervasyon (Independent Action)
**Durum:** Çalışan depoda gezerken bir lens gördü ve hızlıca kendine ayırmak istedi. Proje veya görev oluşturmadan işlem yapmalı.
**İşleyiş:**
1. Çalışan, mobil uygulamadan "QR Okut" butonuna basar.
2. Lens üzerindeki QR kodu okutur.
3. Direkt olarak o ekipmanın detay sayfası açılır.
4. "Rezervasyon Yap" butonuna tıklar, tarih aralığını seçer.
5. **Onay Mekanizması:** Sistem, Ekipman Yöneticisine (Admin/Manager) anlık bildirim gönderir: *"Ahmet, Sony 24-70mm lens için 27 Temmuz'a rezervasyon onayı istiyor."*
6. Yönetici "Onayla" dediğinde rezervasyon kesinleşir.

### 2️⃣ SENARYO: Ekipman Çatışması & Waitlist (Conflict Guard)
**Durum:** Fatih Abi, bir proje için "RED Komodo" kamerasını 27 Temmuz - 10 Ağustos arasına eklemek istiyor. Ancak kamera o tarihlerde dolu.
**İşleyiş:**
1. Sistem, tarih aralığı seçildiğinde veritabanında "Overlap Check" yapar.
2. Kamera listede **PASİF (Gri)** olarak görünür. Üzerinde *"Şu projede kullanımda"* yazar.
3. **Waitlist (Yedek Liste):** Fatih Abi yine de "Sıraya Gir / Waitlist" seçeneğini işaretleyebilir.
4. Eğer öndeki rezervasyon iptal edilirse veya ekipman erken dönerse, sistem otomatik olarak Fatih Abi'ye bildirim gönderir: *"RED Komodo boşa çıktı, hemen rezerve etmek ister misin?"*

### 3️⃣ SENARYO: Mobil Senkronizasyon & Offline Mod
**Durum:** Dağ başında çekim yapan ekipte internet kesildi. Kameraman "Çekim Bitti" ve "Ekipmanları İade Ettim" dedi.
**İşleyiş:**
1. Uygulama veriyi yerel hafızaya (Local Storage) kaydeder.
2. İnternet geldiği anda (Connectivity Event), veriler arka planda sunucuya senkronize edilir (Sync Queue).
3. **Conflict Resolution:** Eğer sunucuda veri değişmişse, "Son Yazan Kazanır" veya "Kullanıcıya Sor" mantığı işler.

### 4️⃣ SENARYO: Canlı Bildirimler (Real-time Event Bus)
**Durum:** Ofisteki Producer revizyon verdiğinde, sahadaki ekibin telefonu anında titremeli.
**İşleyiş:**
1. Producer "Revizyon Gönder"e basar.
2. Backend (Django) bir `Signal` tetikler.
3. WebSocket veya Push Notification servisi (FCM) üzerinden ilgili kullanıcıların cihazlarına anında bildirim gider.
4. Uygulama açık olmasa bile bildirim düşer.

### 5️⃣ SENARYO: Strict Multi-Tenancy (Veri İzolasyonu)
**Durum:** "FilmAdam" ajansının verisi ASLA "VideoKafa" ajansına görünmemeli.
**İşleyiş:**
1. Her veritabanı sorgusunda `tenant_id` filtresi zorunludur.
2. Middleware katmanı, gelen isteğin hangi firmadan geldiğini domain'den (`filmadam.todopro.app`) anlar.
3. Yanlışlıkla bile olsa başka firmanın verisine erişim veritabanı seviyesinde engellenir.

---

## 👥 KULLANICI ROLLERİ

### Platform Seviyesi
- **SUPER_ADMIN**: Platform sahibi (sistem yönetimi, tüm tenant'ları görür)

### Tenant Seviyesi (Firma İçi)

**OWNER (Firma Sahibi)**
- Tüm yetkiler
- Workspace ayarları
- Kullanıcı davet/silme
- Subscription yönetimi
- Fatura bilgileri

**ADMIN (Yönetici)**
- Kullanıcı yönetimi
- Proje oluşturma/silme
- Ekipman ekleme/silme
- Tüm raporlar
- Ayarlar

**MANAGER (Proje Yöneticisi/Producer)**
- Proje yönetimi (atandığı projeler)
- Görev oluşturma/atama
- Ekipman rezervasyonu
- Ekip atama
- Timeline yönetimi
- Proje raporları

**TEAM_LEAD (Ekip Lideri - Opsiyonel)**
- Görev yönetimi (kendi ekibi)
- Ekipman talebi
- Durum güncellemeleri
- Ekip raporları

**TEAM_MEMBER (Ekip Üyesi)**
- Atanan görevleri görür/günceller
- Ekipman check-in/out
- Dosya upload
- Yorum yapma
- Kendi çekimlerini görür

**VIEWER (Sadece Görüntüleme - Opsiyonel)**
- Sadece okuma
- Rapor görüntüleme
- Export

---

## 🏗️ MODÜL PLANI

### **1️⃣ CORE MODULES (Temel Modüller)**

#### 📦 A) Multi-Tenant & Workspace Management
```
✅ Workspace (Firma) Yönetimi
   ├─ Her firma kendi subdomain'i (todopro.app.com)
   ├─ Custom domain bağlama (pro plan)
   ├─ Branding (logo, renkler, email şablonları)
   ├─ Workspace ayarları
   └─ Subscription/Plan yönetimi
   
✅ Kullanıcı & Rol Yönetimi
   ├─ Roller: Owner, Admin, Manager, Team Member, Viewer
   ├─ Özel rol oluşturma (custom roles)
   ├─ Detaylı izinler (granular permissions)
   ├─ Kullanıcı davet sistemi (email)
   ├─ Ekip grupları (departments: Kamera Ekibi, Işık Ekibi, vs.)
   └─ Kullanıcı profilleri (beceriler, sertifikalar, deneyim)
```

#### 🔐 B) Authentication & Security
```
✅ Güvenlik
   ├─ JWT Authentication
   ├─ 2FA (Two-Factor Authentication)
   ├─ Session yönetimi
   ├─ IP whitelist/blacklist
   ├─ Activity logs (kim ne yaptı)
   ├─ GDPR compliance
   └─ Role-based access control (RBAC)
```

---

### **2️⃣ PROJECT & TASK MANAGEMENT (ClickUp-Style)**

#### 📋 C) Proje Yönetimi
```
✅ Proje/İş Modülü
   ├─ Proje oluşturma (müşteri, bütçe, tarih)
   ├─ Proje şablonları (Reklam Çekimi, Kurumsal Video, vs.)
   ├─ Proje tipleri/kategoriler
   ├─ Alt projeler (sub-projects)
   ├─ Proje durumları (custom statuses)
   ├─ Proje öncelikleri (Düşük, Orta, Yüksek, Kritik)
   ├─ Proje etiketleri (tags)
   ├─ Proje milestone'ları (önemli başarılar)
   ├─ Müşteri bilgileri integration
   └─ Proje arşivleme
   
✅ Görev Yönetimi (Tasks)
   ├─ Görev oluşturma (başlık, açıklama, deadline)
   ├─ Alt görevler (subtasks)
   ├─ Görev bağımlılıkları (Task A bitmeden Task B başlamasın)
   ├─ Tekrarlayan görevler (recurring tasks)
   ├─ Görev şablonları
   ├─ Görev ataması (tek veya çoklu kişi)
   ├─ Görev durumları (To Do, In Progress, Review, Done, Blocked)
   ├─ Görev öncelikleri
   ├─ Görev etiketleri
   ├─ Tahmini süre (time estimate)
   ├─ Gerçek süre (time tracking)
   ├─ Checklist (yapılacaklar listesi)
   └─ Custom fields (özel alanlar)
```

#### 📊 D) Görünümler (Views)
```
✅ Farklı Görüntüleme Modları
   ├─ 📋 Liste Görünümü (List View)
   ├─ 📊 Kanban Board (Trello-style)
   ├─ 📅 Takvim Görünümü (Calendar)
   ├─ 📈 Gantt Chart (Timeline)
   ├─ 📌 Board View (Grup bazlı)
   ├─ 📑 Tablo Görünümü (Table/Spreadsheet)
   └─ 🗺️ Lokasyon Haritası (çekim yerleri)
```

---

### **3️⃣ EQUIPMENT MANAGEMENT ⭐ (KILLER FEATURE)**

#### 🎥 E) Ekipman Yönetimi
```
✅ Ekipman Envanteri
   ├─ Kategoriler (Kamera, Lens, Işık, Ses, Drone, Aksesuarlar)
   ├─ Alt kategoriler
   ├─ Ekipman ekleme (marka, model, seri no)
   ├─ Ekipman özellikleri (specs)
   ├─ Ekipman fotoğrafları
   ├─ QR kod/barkod (hızlı scan)
   ├─ RFID entegrasyonu (gelişmiş)
   ├─ Satın alma bilgisi (tarih, fiyat, tedarikçi)
   ├─ Garanti bilgisi
   ├─ Amortisman takibi
   ├─ Sigorta bilgileri
   └─ Ekipman grupları/setler (paket olarak ata)
   
✅ Rezervasyon & Atama
   ├─ Ekipman rezervasyon sistemi
   ├─ Müsaitlik takvimi
   ├─ Çakışma (conflict) kontrolü
   ├─ Otomatik rezervasyon onayı/reddi
   ├─ Bekleyen rezervasyonlar
   ├─ Check-out (ekipmanı al)
   ├─ Check-in (ekipmanı iade et)
   ├─ Check-in sırasında durum kontrolü (hasarlı mı?)
   ├─ Geç iade uyarıları
   ├─ Ekipman geçmişi (kim ne zaman kullandı)
   └─ Kiralama entegrasyonu (dışarıdan kiralanan ekipmanlar)
   
✅ Bakım & Servis
   ├─ Periyodik bakım planı
   ├─ Bakım geçmişi
   ├─ Arıza kayıtları
   ├─ Servis talepleri
   ├─ Servis süreci takibi
   ├─ Bakım maliyetleri
   ├─ Yedek parça takibi
   └─ Bakım hatırlatmaları (otomatik)
   
✅ Depo Yönetimi
   ├─ Fiziksel lokasyonlar (Depo A, Raf 3, vs.)
   ├─ Depo transfer işlemleri
   ├─ Stok sayımı
   ├─ Minimum stok uyarıları
   ├─ Sarf malzemeler (pil, tape, vs.)
   ├─ Otomatik sipariş önerileri
   └─ Multi-location support (birden fazla depo)
```

---

### **4️⃣ RESOURCE MANAGEMENT**

#### 👥 F) İnsan Kaynakları & Ekip
```
✅ Personel Yönetimi
   ├─ Çalışan profilleri (beceriler, sertifikalar)
   ├─ Uzmanlık alanları (kameraman, ışıkçı, ses, vs.)
   ├─ Deneyim seviyesi (junior, mid, senior)
   ├─ Müsaitlik takvimi
   ├─ İzin/tatil yönetimi
   ├─ Shift/vardiya planlama
   ├─ Çalışan performans raporları
   ├─ Eğitim kayıtları
   └─ Sertifikasyon takibi
   
✅ Freelancer/Harici Ekip
   ├─ Freelancer havuzu
   ├─ Derecelendirme sistemi (rating)
   ├─ Freelancer müsaitliği
   ├─ Freelancer fiyatlandırması
   └─ Geçmiş iş birliği kayıtları
```

#### 📍 G) Lokasyon Yönetimi
```
✅ Çekim Yerleri
   ├─ Lokasyon kütüphanesi
   ├─ Lokasyon detayları (adres, izinler, notlar)
   ├─ Lokasyon fotoğrafları
   ├─ Harita entegrasyonu (Google Maps)
   ├─ Lokasyon müsaitliği
   ├─ İzin/permit takibi
   ├─ Lokasyon maliyetleri
   └─ Favoriler
```

---

### **5️⃣ SCHEDULING & CALENDAR**

#### 📅 H) Takvim & Planlama
```
✅ Akıllı Takvim
   ├─ Birleşik takvim (projeler, ekip, ekipman)
   ├─ Kişisel takvim
   ├─ Ekip takvimi
   ├─ Ekipman rezervasyon takvimi
   ├─ Çakışma kontrolü
   ├─ Drag & drop planlama
   ├─ Takvim paylaşımı
   ├─ iCal export (Google Calendar sync)
   ├─ Zaman dilimi desteği
   └─ Tatil/özel günler
   
✅ Shooting Schedule (Çekim Programı)
   ├─ Günlük çekim planı
   ├─ Scene/sahne bazlı planlama
   ├─ Call sheet (çekim çağrı formu)
   ├─ Günlük rapor (daily production report)
   └─ PDF export
```

---

### **6️⃣ COLLABORATION & COMMUNICATION**

#### 💬 I) İş Birliği Araçları
```
✅ İletişim
   ├─ Görev yorumları (comments)
   ├─ @mentions (bildirim gönder)
   ├─ Gerçek zamanlı bildirimler
   ├─ Email bildirimleri
   ├─ Push notifications (mobil)
   ├─ SMS bildirimleri (opsiyonel)
   ├─ Dahili mesajlaşma (team chat)
   ├─ Proje announcement'ları
   └─ File sharing (dosya paylaşımı)
   
✅ Dosya Yönetimi
   ├─ Dosya yükleme (video, fotoğraf, döküman)
   ├─ Klasör yapısı
   ├─ Versiyon kontrolü (v1, v2, vs.)
   ├─ Dosya önizleme
   ├─ Video player (embedded)
   ├─ Dosya paylaşım linkleri
   ├─ Dosya izinleri (kim görebilir)
   ├─ Toplu indirme (bulk download)
   ├─ Cloud storage entegrasyonu (S3, Dropbox, Google Drive)
   └─ Otomatik yedekleme
```

---

### **7️⃣ CLIENT MANAGEMENT**

#### 🤝 J) Müşteri İlişkileri (CRM)
```
✅ Müşteri Yönetimi
   ├─ Müşteri veritabanı
   ├─ Şirket/kişi bilgileri
   ├─ İletişim bilgileri
   ├─ Müşteri notları
   ├─ Müşteri geçmişi (önceki projeler)
   ├─ Müşteri segmentasyonu
   ├─ Müşteri portalı (opsiyonel - müşteri giriş yapıp işini görebilir)
   └─ Müşteri memnuniyeti anketi
   
✅ Teklif & Sözleşme
   ├─ Teklif oluşturma
   ├─ Teklif şablonları
   ├─ PDF export
   ├─ Online onay sistemi (e-imza)
   ├─ Sözleşme yönetimi
   └─ Sözleşme hatırlatıcıları
```

---

### **8️⃣ FINANCIAL MANAGEMENT**

#### 💰 K) Finans & Bütçe
```
✅ Bütçe Yönetimi
   ├─ Proje bütçesi (tahmini maliyet)
   ├─ Gerçek maliyet takibi
   ├─ Bütçe kategorileri (ekipman, personel, lokasyon, vs.)
   ├─ Bütçe vs. gerçek karşılaştırması
   ├─ Kar/zarar analizi
   └─ Bütçe onay süreci
   
✅ Faturalandırma
   ├─ Fatura oluşturma
   ├─ Fatura şablonları
   ├─ Otomatik fatura numaralandırma
   ├─ KDV hesaplama
   ├─ Ödeme takibi (ödendi/ödenmedi)
   ├─ Tahsilat hatırlatmaları
   ├─ Banka entegrasyonu (opsiyonel)
   ├─ E-fatura entegrasyonu (Türkiye için)
   └─ Muhasebe yazılımı exportu
   
✅ Gider Yönetimi
   ├─ Gider kayıtları
   ├─ Gider kategorileri
   ├─ Projeye gider atama
   ├─ Gider onay süreci
   ├─ Makbuz/fiş yükleme
   └─ Gider raporları
   
✅ Ödeme & Bordro
   ├─ Freelancer ödemeleri
   ├─ Ödeme geçmişi
   ├─ Ödeme hatırlatıcıları
   └─ Çalışan bordro entegrasyonu (gelişmiş)
```

---

### **9️⃣ REPORTING & ANALYTICS**

#### 📊 L) Raporlama & Analitik
```
✅ Dashboard
   ├─ Genel durum özeti
   ├─ KPI'lar (Key Performance Indicators)
   ├─ Widget'lar (özelleştirilebilir)
   ├─ Grafik/chart'lar
   └─ Gerçek zamanlı veri
   
✅ Raporlar
   ├─ Proje raporları (durum, ilerleme)
   ├─ Ekipman kullanım raporları
   ├─ Ekip performans raporları
   ├─ Finans raporları (gelir/gider)
   ├─ Zaman takibi raporları
   ├─ Müşteri raporları
   ├─ Özel rapor oluşturma
   ├─ Rapor filtreleme (tarih, proje, kişi)
   ├─ PDF/Excel export
   └─ Otomatik rapor gönderimi (email)
   
✅ Analytics
   ├─ Trend analizleri
   ├─ Tahminsel analiz (predictive)
   ├─ Verimlilik metrikleri
   ├─ Karşılaştırmalı analizler
   └─ Özelleştirilebilir metrikler
```

---

### **🔟 ADVANCED FEATURES**

#### 🤖 M) Otomasyon & AI
```
✅ Workflow Automation
   ├─ Otomatik görev atamaları
   ├─ Durum değiştiğinde aksiyon (status → action)
   ├─ Trigger'lar (X olduğunda Y yap)
   ├─ Email otomasyonları
   ├─ Hatırlatıcılar
   └─ Webhook entegrasyonları
   
✅ AI Özellikleri (İleri Seviye)
   ├─ Akıllı görev önerileri
   ├─ Otomatik scheduling (AI planlama)
   ├─ Bütçe tahminleri
   ├─ Risk analizi
   ├─ Doğal dil ile görev oluşturma
   └─ AI asistan (chatbot)
```

#### 📱 N) Mobil & Offline
```
✅ Mobil Uygulama
   ├─ iOS & Android native apps (gelecek)
   ├─ PWA (Progressive Web App) - şimdilik
   ├─ Offline mode
   ├─ Push notifications
   ├─ QR kod scanner
   ├─ Fotoğraf/video çekimi direkt uygulama içinde
   ├─ GPS lokasyon paylaşımı (gerçek zamanlı)
   └─ Mobil-optimized UI
```

#### 🔗 O) Entegrasyonlar
```
✅ Third-Party Integrations
   ├─ Google Workspace (Calendar, Drive)
   ├─ Microsoft 365 (Outlook, OneDrive)
   ├─ Slack
   ├─ WhatsApp Business API
   ├─ Dropbox
   ├─ Payment gateways (Stripe, Iyzico)
   ├─ E-fatura (Türkiye)
   ├─ Muhasebe yazılımları (Paraşüt, vs.)
   ├─ CRM'ler (HubSpot, Salesforce)
   └─ Custom API (diğer sistemlerle)
```

#### 🎨 P) Özelleştirme
```
✅ Customization
   ├─ Özel alanlar (custom fields)
   ├─ Özel durum akışları (custom workflows)
   ├─ Özel roller ve izinler
   ├─ Tema özelleştirme (renk, logo)
   ├─ Email şablonları
   ├─ PDF şablonları
   └─ White-label (gelişmiş plan)
```

---

### **1️⃣1️⃣ SYSTEM & ADMIN**

#### ⚙️ Q) Sistem Yönetimi
```
✅ Admin Panel
   ├─ Tüm tenant'ları görme
   ├─ Subscription yönetimi
   ├─ Faturalandırma
   ├─ System health monitoring
   ├─ Performance metrikleri
   ├─ Hata logları
   └─ Backup yönetimi
   
✅ Güvenlik & Compliance
   ├─ Audit logs (tüm aktiviteler)
   ├─ Data export (GDPR)
   ├─ Data deletion
   ├─ Privacy settings
   ├─ Terms & conditions
   └─ Compliance raporları
```

---

## 🎯 MODÜL ÖNCELİKLENDİRME

### **PHASE 1 - MVP (3-4 ay)**
```
✅ A - Multi-Tenant & Workspace
✅ B - Authentication & Security
✅ C - Proje & Görev Yönetimi (Temel)
✅ D - Görünümler (Liste, Kanban, Takvim)
✅ E - Ekipman Yönetimi (Check-in/out, Rezervasyon)
✅ F - Personel Yönetimi (Temel)
✅ I - Dosya Yönetimi & Yorumlar
✅ L - Temel Dashboard & Raporlar
✅ N - Mobil Responsive (PWA)
```

### **PHASE 2 - Advanced (2-3 ay)**
```
✅ E - Ekipman (Bakım, Depo)
✅ G - Lokasyon Yönetimi
✅ H - Gelişmiş Takvim & Shooting Schedule
✅ J - CRM & Müşteri Yönetimi
✅ K - Finans & Bütçe
✅ L - Gelişmiş Raporlar & Analytics
✅ M - Temel Otomasyon
✅ P - Özelleştirme
```

### **PHASE 3 - Enterprise (2-3 ay)**
```
✅ M - AI Özellikleri
✅ N - Native Mobil Apps
✅ O - Entegrasyonlar
✅ P - White-label
✅ Advanced Analytics
✅ Multi-language support
```

---

## 💡 EK FİKİRLER

1. **Gamification**: Görev tamamlama puanı, başarı rozetleri
2. **Social Feed**: Şirket içi sosyal feed (kim ne yaptı)
3. **Knowledge Base**: Firma içi wiki, dokümantasyon
4. **Training Module**: Ekip eğitimleri, sertifikalar
5. **Time Tracking**: Geçirilen süre takibi (manuel veya otomatik)
6. **Video Conferencing**: Entegre görüşme (Zoom/Teams benzeri)

---

## 🏗️ TEKNOLOJİ STACK

### Backend
- **Framework**: Django 5.x + Django REST Framework
- **Database**: PostgreSQL (multi-tenant support)
- **Cache**: Redis
- **Task Queue**: Celery + Redis
- **File Storage**: AWS S3 / Cloudinary
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend (Ayrı Repo)
- **Framework**: Next.js 14+ (App Router)
- **Styling**: TailwindCSS + shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: React Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts / Chart.js

### DevOps
- **Containerization**: Docker + Docker Compose
- **Deployment**: AWS / DigitalOcean / Hetzner
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (error tracking)

---

## 📂 BACKEND PROJE YAPISI

```
todo-backend/
├── config/                     # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── tenants/               # Multi-tenant yönetimi
│   ├── users/                 # Kullanıcı & Auth
│   ├── projects/              # Proje yönetimi
│   ├── tasks/                 # Görev yönetimi
│   ├── equipment/             # Ekipman yönetimi
│   ├── inventory/             # Depo/stok
│   ├── calendar/              # Takvim & Rezervasyon
│   ├── files/                 # Dosya yönetimi
│   ├── clients/               # CRM/Müşteri yönetimi
│   ├── finance/               # Finans & Bütçe
│   ├── notifications/         # Bildirimler
│   └── analytics/             # Raporlar & Analytics
│
├── core/                      # Shared utilities
│   ├── permissions.py         # Custom permissions
│   ├── middleware.py          # Tenant middleware
│   ├── mixins.py              # Reusable mixins
│   ├── utils.py               # Helper functions
│   └── exceptions.py          # Custom exceptions
│
├── tests/                     # Test'ler
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── manage.py
└── README.md
```

---

## 🗄️ VERİ MODELLERİ (Database Schema)

### 1. Tenant (Firma/Workspace)
```python
- id
- name (string)
- slug (string, unique)
- subdomain (string, unique)
- custom_domain (string, nullable)
- logo_url (string)
- plan (choices: free, pro, enterprise)
- is_active (boolean)
- settings (JSON)
- created_at, updated_at
```

### 2. User (Kullanıcı)
```python
- id
- email (unique)
- first_name, last_name
- phone
- avatar_url
- is_active
- last_login
- created_at, updated_at
```

### 3. TenantMembership (Kullanıcı-Tenant İlişkisi)
```python
- id
- user_id (FK)
- tenant_id (FK)
- role (choices: owner, admin, manager, member, viewer)
- is_active
- joined_at
- unique_together: (user, tenant)
```

### 4. Project (Proje/İş)
```python
- id
- tenant_id (FK)
- title
- description (text)
- client_id (FK, nullable)
- project_type (string)
- status (choices: planned, in_progress, review, completed, cancelled)
- priority (choices: low, medium, high, critical)
- budget_estimated (decimal)
- budget_actual (decimal)
- start_date, end_date
- location
- tags (JSON array)
- custom_fields (JSON)
- created_by (FK User)
- assigned_to (M2M User)
- created_at, updated_at
```

### 5. Task (Görev)
```python
- id
- tenant_id (FK)
- project_id (FK)
- parent_task_id (FK, nullable - alt görevler için)
- title
- description (text)
- status (string, customizable)
- priority
- assigned_to (M2M User)
- tags (JSON)
- due_date
- time_estimate (integer, minutes)
- time_actual (integer, minutes)
- checklist (JSON)
- dependencies (M2M Task)
- custom_fields (JSON)
- created_by (FK User)
- created_at, updated_at
```

### 6. Equipment (Ekipman)
```python
- id
- tenant_id (FK)
- category (string)
- name
- brand, model
- serial_number (unique)
- description
- specifications (JSON)
- images (JSON array)
- qr_code (string)
- status (choices: available, in_use, maintenance, retired)
- purchase_date, purchase_price
- warranty_expiry
- insurance_info (JSON)
- current_location (string)
- created_at, updated_at
```

### 7. EquipmentReservation (Ekipman Rezervasyonu)
```python
- id
- tenant_id (FK)
- equipment_id (FK)
- project_id (FK, nullable)
- task_id (FK, nullable)
- reserved_by (FK User)
- start_date, end_date
- status (choices: pending, approved, active, completed, cancelled)
- notes (text)
- created_at, updated_at
```

### 8. EquipmentCheckout (Check-in/out)
```python
- id
- reservation_id (FK)
- equipment_id (FK)
- user_id (FK)
- checked_out_at (datetime)
- checked_in_at (datetime, nullable)
- condition_out (string)
- condition_in (string, nullable)
- notes (text)
```

### 9. Client (Müşteri)
```python
- id
- tenant_id (FK)
- company_name
- contact_person
- email, phone
- address
- notes (text)
- tags (JSON)
- created_at, updated_at
```

### 10. File (Dosya)
```python
- id
- tenant_id (FK)
- project_id (FK, nullable)
- task_id (FK, nullable)
- uploaded_by (FK User)
- file_name
- file_url
- file_type (string)
- file_size (integer)
- version (integer)
- folder_path (string)
- created_at
```

### 11. Comment (Yorum)
```python
- id
- tenant_id (FK)
- content_type (FK) # Generic relation
- object_id (integer)
- user_id (FK)
- content (text)
- mentions (M2M User)
- created_at, updated_at
```

### 12. Notification (Bildirim)
```python
- id
- tenant_id (FK)
- user_id (FK)
- notification_type (string)
- title
- message
- link (string)
- is_read (boolean)
- created_at
```

---

## 🔐 PERMİSSİON MATRİXİ

| **Özellik** | Owner | Admin | Manager | Member | Viewer |
|------------|:-----:|:-----:|:-------:|:------:|:------:|
| Workspace Ayarları | ✅ | ❌ | ❌ | ❌ | ❌ |
| Kullanıcı Ekle/Sil | ✅ | ✅ | ❌ | ❌ | ❌ |
| Proje Oluştur/Sil | ✅ | ✅ | ✅ | ❌ | ❌ |
| Görev Oluştur | ✅ | ✅ | ✅ | ❌ | ❌ |
| Görev Güncelle (Atanan) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Ekipman Ekle/Sil | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ekipman Rezerve Et | ✅ | ✅ | ✅ | ✅ | ❌ |
| Ekipman Check-in/out | ✅ | ✅ | ✅ | ✅ | ❌ |
| Dosya Upload | ✅ | ✅ | ✅ | ✅ | ❌ |
| Raporlar (Tümü) | ✅ | ✅ | ✅ | ❌ | ✅ |
| Finans Görüntüleme | ✅ | ✅ | ❌ | ❌ | ❌ |
| Faturalandırma | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 📱 MOBİL KULLANIM

### Çalışanın Mobil Görünümü

**Ana Ekran:**
```
┌─────────────────────────────┐
│  📱 Bugünkü İşlerim         │
├─────────────────────────────┤
│ 🔴 ACIL - 09:00             │
│ "X Marka Reklam Çekimi"     │
│ 📍 Maslak Studio            │
│ 🎥 Kameraman                │
│ [Detaylar] [Başlat]         │
├─────────────────────────────┤
│ 🟡 DEVAM EDİYOR - 14:00     │
│ "Y Firması Tanıtım"         │
│ 📍 Bebek Sahil              │
│ 💡 Işıkçı                   │
│ [Durum Güncelle]            │
└─────────────────────────────┘
```

**Görev Detayı:**
```
┌─────────────────────────────┐
│ 📋 İş Detayı                │
├─────────────────────────────┤
│ Proje: X Marka Reklam       │
│ Tarih: 18.01.2026, 09:00    │
│ Lokasyon: Maslak Studio     │
│                             │
│ 👥 Ekip:                    │
│ • Ahmet (Kameraman) ← Sen   │
│ • Mehmet (Işıkçı)           │
│                             │
│ 🎥 Ekipmanlar:              │
│ • Sony A7S III (#12345)     │
│ • 24-70mm Lens (#67890)     │
│ [Ekipmanları Al]            │
│                             │
│ 🔄 Durum:                   │
│ [Lokasyona Gittim]          │
│ [Çekime Başladım]           │
│ [Tamamladım]                │
└─────────────────────────────┘
```

---

## 🎨 TASARIM PRENSİPLERİ

1. **Mobil-First**: Önce mobil tasarla
2. **Dark Mode**: Profesyonel sinematik görünüm
3. **Minimal & Clean**: Az yazı, çok görsel
4. **Hızlı Aksiyon**: Büyük butonlar
5. **Renk Kodlama**: Durumlara göre renk (🔴 Acil, 🟡 Devam, 🟢 Tamamlandı)

---

## 🚀 SONRAKI ADIMLAR

1. ✅ Proje planı oluşturuldu
2. [ ] Database schema detaylandır
3. [ ] API endpoint'leri planla
4. [ ] Django proje yapısını oluştur
5. [ ] İlk modül (Multi-tenant) geliştir
6. [ ] Authentication sistemi
7. [ ] Proje & Task yönetimi
8. [ ] Ekipman yönetimi
9. [ ] Frontend entegrasyonu
10. [ ] Test & Deploy

---

**Son Güncelleme:** 18.01.2026  
**Hazırlayan:** Antigravity AI  
**Proje Durumu:** Planlama Aşaması
