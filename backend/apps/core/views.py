from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class AgencyModelViewSet(viewsets.ModelViewSet):
    """
    Sadece kullanıcının aktif ajansına ait verileri getiren Base ViewSet.
    Strict Multi-Tenancy sağlar.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Eğer admin değilse ve ajansı yoksa boş liste dön
        if not user.current_agency and not user.is_staff:
            return self.queryset.none()
        
        # Sadece kendi ajansının verilerini getir
        return self.queryset.filter(agency=user.current_agency)

    def perform_create(self, serializer):
        # Kaydederken hem agency'i hem de created_by'ı otomatik ata
        save_kwargs = {'agency': self.request.user.current_agency}
        
        # Eğer modelde 'created_by' alanı varsa, kullanıcıyı ata
        if hasattr(serializer.Meta.model, 'created_by'):
            save_kwargs['created_by'] = self.request.user
            
        serializer.save(**save_kwargs)
