from django.db import models
from apps.agencies.models import AgencyAwareModel

class EquipmentCategory(AgencyAwareModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Ekipman Kategorisi"
        verbose_name_plural = "Ekipman Kategorileri"

    def __str__(self):
        return self.name
