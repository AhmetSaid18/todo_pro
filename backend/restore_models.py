import os

def append_to_file(path, content):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n' + content + '\n')
        print(f"Appended to {path}")
    except Exception as e:
        print(f"Error appending to {path}: {e}")

# 1. Client -> apps.agencies.models
client_code = """
class Client(AgencyAwareModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    tax_office = models.CharField(max_length=100, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
"""
append_to_file(r'c:\projects\todo\backend\apps\agencies\models.py', client_code)

# 2. Location, File, Expense, Schedule -> apps.projects.models
project_extras_code = """
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
"""
append_to_file(r'c:\projects\todo\backend\apps\projects\models.py', project_extras_code)

# 3. Notification, Audit -> apps.users.models
users_extras_code = """
from apps.agencies.models import AgencyAwareModel

class Notification(AgencyAwareModel):
    TYPE_CHOICES = (
        ('info', 'Bilgi'),
        ('warning', 'Uyarı'),
        ('success', 'Başarı'),
        ('error', 'Hata'),
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.recipient.email} - {self.title}"

class AuditLog(AgencyAwareModel):
    ACTION_CHOICES = (
        ('create', 'Oluşturma'),
        ('update', 'Güncelleme'),
        ('delete', 'Silme'),
        ('login', 'Giriş'),
        ('logout', 'Çıkış'),
        ('other', 'Diğer'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    changes = models.JSONField(default=dict, blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user} - {self.action}"
"""
append_to_file(r'c:\projects\todo\backend\apps\users\models.py', users_extras_code)
