from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel
from apps.agencies.models import Agency, AgencyRole

class User(AbstractUser, BaseModel):
    """
    Sistem genelindeki kullanıcı modeli.
    """
    email = models.EmailField(unique=True, verbose_name="E-posta Adresi")
    
    # Kullanıcının şu an aktif olduğu ajans
    current_agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_users')
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Global Admin (Süper kullanıcı) vs Ajans kullanıcısı ayrımı için
    is_platform_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class AgencyMembership(BaseModel):
    """
    Kullanıcının ajanla olan bağı.
    Burada kullanıcıya ESNEK ROL (AgencyRole) atanır.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='memberships')
    
    # Esnek Rol Ataması
    role = models.ForeignKey(AgencyRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    # Ajans Sahibi mi? (Rollerden bağımsız, en üst yetki)
    is_owner = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'agency')
        verbose_name = "Ajans Üyeliği"

    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        status = "Owner" if self.is_owner else role_name
        return f"{self.user.email} -> {self.agency.name} ({status})"


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

