from django.db import models
from apps.core.models import BaseModel
from apps.agencies.models import AgencyAwareModel
from apps.users.models import User

class Project(AgencyAwareModel):
    """
    Project (İş) Modeli.
    Bir reklam filmi, klip veya photoshoot olabilir.
    """
    STATUS_CHOICES = (
        ('standard_planning', 'Planlama'),
        ('active_production', 'Prodüksiyon'),
        ('post_production', 'Post-Prodüksiyon'),
        ('review_client', 'Müşteri Onayı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Acil'),
    )

    title = models.CharField(max_length=255, verbose_name="Proje Başlığı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Müşteri (Şimdilik string, ileride Client modeline bağlanabilir)
    client_name = models.CharField(max_length=255, blank=True, verbose_name="Müşteri")
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='standard_planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    # Bütçe
    budget_estimated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # İlişkiler
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    assigned_team = models.ManyToManyField(User, blank=True, related_name='assigned_projects')
    
    tags = models.JSONField(default=list, blank=True) # ["Klip", "Dış Çekim"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Location(AgencyAwareModel):
    name = models.CharField(max_length=255, verbose_name="Lokasyon Adı")
    address = models.TextField(blank=True)
    google_maps_url = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    access_details = models.TextField(blank=True, verbose_name="Giriş/Ulaşım Bilgileri")
    images = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

class File(AgencyAwareModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    file = models.FileField(upload_to='project_files/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.BigIntegerField(default=0)
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.original_name

class ExpenseCategory(AgencyAwareModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    class Meta:
        verbose_name_plural = "Expense Categories"
    def __str__(self):
        return self.name

class Expense(AgencyAwareModel):
    STATUS_CHOICES = (
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('paid', 'Ödendi'),
        ('rejected', 'Reddedildi'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name='expenses')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    description = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255, blank=True)
    invoice_no = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attachment = models.FileField(upload_to='expenses/', null=True, blank=True)
    def __str__(self):
        return f"{self.project.title} - {self.description}"

class ShootingDay(AgencyAwareModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='shooting_days')
    date = models.DateField()
    call_time = models.TimeField()
    wrap_time = models.TimeField(null=True, blank=True)
    main_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['date']
    def __str__(self):
        return f"{self.project.title} - {self.date}"

class CallSheet(AgencyAwareModel):
    shooting_day = models.OneToOneField(ShootingDay, on_delete=models.CASCADE, related_name='call_sheet')
    sent_to_crew = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='callsheets/', null=True, blank=True)
    data = models.JSONField(default=dict)
    def __str__(self):
        return f"Call Sheet - {self.shooting_day}"

class FileTransfer(AgencyAwareModel):
    STATUS_CHOICES = (
        ('uploading', 'Yükleniyor'),
        ('active', 'Aktif'),
        ('expired', 'Süresi Doldu'),
        ('downloaded', 'İndirildi'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transfers')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transfers')
    
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    
    recipient_email = models.EmailField(blank=True)
    download_link = models.URLField(blank=True) 
    
    files = models.JSONField(default=list) 
    
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    download_count = models.IntegerField(default=0)
    total_size_bytes = models.BigIntegerField(default=0)
    password = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.title
