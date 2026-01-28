from django.db import models
from apps.core.models import BaseModel

class Agency(BaseModel):
    """
    Agency (Eski adıyla Tenant).
    Her prodüksiyon firması bir Agency'dir.
    """
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    )

    name = models.CharField(max_length=255, verbose_name="Ajans Adı")
    slug = models.SlugField(unique=True, verbose_name="URL Slug")
    subdomain = models.CharField(max_length=63, unique=True, null=True, blank=True)
    
    logo = models.ImageField(upload_to='agency_logos/', null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Ajans"
        verbose_name_plural = "Ajanslar"

    def __str__(self):
        return self.name

class AgencyRole(BaseModel):
    """
    Her ajansın kendi tanımladığı dinamik roller.
    Örn: "Head of Production", "Kameraman", "Stajyer"
    """
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100, verbose_name="Rol Adı") # Örn: Kameraman
    color = models.CharField(max_length=7, default="#000000") # UI'da göstermek için
    
    # Yetkiler (Permissions) - Granular control
    can_manage_projects = models.BooleanField(default=False)
    can_manage_team = models.BooleanField(default=False)
    can_manage_equipment = models.BooleanField(default=False)
    can_view_finance = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False) # Admin yetkisi gibi
    
    class Meta:
        unique_together = ('agency', 'name')
        verbose_name = "Rol"

    def __str__(self):
        return f"{self.name} ({self.agency.name})"

class AgencyAwareModel(BaseModel):
    """
    Ajansa bağlı her model bu sınıfı miras almalı.
    """
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="%(class)s_set")

    class Meta:
        abstract = True


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

