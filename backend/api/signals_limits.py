from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from api.models import Project, AgencyMembership, User

@receiver(pre_save, sender=Project)
def check_project_limit(sender, instance, **kwargs):
    """
    Yeni proje oluşturulurken ajansın proje limitini kontrol et.
    """
    if instance._state.adding: # Sadece yeni kayıtta (Update hariç)
        agency = instance.agency
        
        # Enterprise ise limit yok
        if agency.plan == 'enterprise':
            return

        current_count = Project.objects.filter(agency=agency).count()
        if current_count >= agency.max_projects:
            raise ValidationError(f"Proje limitiniz ({agency.max_projects}) doldu. Lütfen paketinizi yükseltin.")

@receiver(pre_save, sender=AgencyMembership)
def check_user_limit(sender, instance, **kwargs):
    """
    Yeni kullanıcı eklenirken ajansın kullanıcı limitini kontrol et.
    """
    if instance._state.adding:
        agency = instance.agency
        
        if agency.plan == 'enterprise':
            return
            
        # Active üyeleri say
        current_count = AgencyMembership.objects.filter(agency=agency, is_active=True).count()
        if current_count >= agency.max_users:
            raise ValidationError(f"Kullanıcı limitiniz ({agency.max_users}) doldu. Lütfen paketinizi yükseltin.")
