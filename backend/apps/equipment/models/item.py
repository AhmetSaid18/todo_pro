from django.db import models
from apps.agencies.models import AgencyAwareModel
from apps.users.models import User
from .category import EquipmentCategory

class Equipment(AgencyAwareModel):
    """
    Ekipman Envanteri.
    Kamera, Lens, Işık vs.
    """
    STATUS_CHOICES = (
        ('available', 'Müsait'),
        ('in_use', 'Kullanımda/Sahada'),
        ('maintenance', 'Bakımda'),
        ('retired', 'Hurda/Emekli'),
    )

    category = models.ForeignKey(EquipmentCategory, on_delete=models.SET_NULL, null=True, related_name='equipment')
    name = models.CharField(max_length=255, verbose_name="Ekipman Adı") # Sony A7S III
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Seri No")
    qr_code = models.CharField(max_length=255, unique=True, verbose_name="QR Code Data")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Şu an kimde?
    current_holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='holding_equipment')
    
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    images = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Ekipman"
        verbose_name_plural = "Ekipmanlar"

    def __str__(self):
        return f"{self.name} ({self.status})"
