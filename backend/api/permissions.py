from rest_framework import permissions
from api.models import AgencyMembership

class HasAgencyPermission(permissions.BasePermission):
    """
    Kullanıcının ajansta gerekli yetkiye sahip olup olmadığını kontrol eder.
    View'da 'required_role_permission' özelliği tanımlanmalıdır.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Admin ise her yetkisi vardır
        if request.user.is_staff or request.user.is_platform_admin:
            return True

        # Ajansı yoksa reddet
        if not request.user.current_agency:
            return False

        # View'da özel bir permission istenmemişse geç
        required_perm = getattr(view, 'required_role_permission', None)
        if not required_perm:
            return True

        # Kullanıcının ajans üyeliğini ve rolünü bul
        try:
            membership = AgencyMembership.objects.select_related('role').get(
                user=request.user,
                agency=request.user.current_agency
            )
        except AgencyMembership.DoesNotExist:
            return False

        # Owner ise her şeye yetkisi var
        if membership.is_owner:
            return True

        # Rolü yoksa (ve owner değilse) yetkisiz
        if not membership.role:
            return False
            
        # İstenen yetkiyi kontrol et (örn: role.can_manage_projects)
        return getattr(membership.role, required_perm, False)
