from django.db import models
from apps.agencies.models import AgencyAwareModel
from apps.users.models import User
from apps.projects.models import Project
from .item import Equipment

class EquipmentReservation(AgencyAwareModel):
    """
    Rezervasyon Tablosu.
    Geleceğe yönelik planlama.
    """
    STATUS_CHOICES = (
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('active', 'Aktif (Teslim Alındı)'),
        ('completed', 'Tamamlandı (İade Edildi)'),
        ('cancelled', 'İptal'),
    )

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='reservations')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment_reservations')
    
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Rezervasyon"
        verbose_name_plural = "Rezervasyonlar"

    def __str__(self):
        return f"{self.equipment.name} -> {self.reserved_by.email} ({self.status})"
