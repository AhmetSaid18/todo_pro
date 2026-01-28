from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import AuditLog
import json

class AgencyModelViewSet(viewsets.ModelViewSet):
    """
    Sadece kullanıcının aktif ajansına ait verileri getiren Base ViewSet.
    + Automatic Audit Logging
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.current_agency and not user.is_staff:
            return self.queryset.none()
        return self.queryset.filter(agency=user.current_agency)

    def log_action(self, action, instance, changes=None):
        try:
            AuditLog.objects.create(
                agency=self.request.user.current_agency,
                action=action,
                model_name=instance._meta.model_name,
                object_id=str(instance.id),
                object_repr=str(instance),
                user=self.request.user,
                changes=changes or {}
            )
        except Exception:
            pass # Log başarısız olursa işlem durmasın

    def perform_create(self, serializer):
        save_kwargs = {'agency': self.request.user.current_agency}
        if hasattr(serializer.Meta.model, 'created_by'):
            save_kwargs['created_by'] = self.request.user
        instance = serializer.save(**save_kwargs)
        self.log_action('create', instance)

    def perform_update(self, serializer):
        # Değişiklikleri yakalamak zor ama basitçe loglayalım
        instance = serializer.save()
        self.log_action('update', instance)

    def perform_destroy(self, instance):
        self.log_action('delete', instance)
        instance.delete()
