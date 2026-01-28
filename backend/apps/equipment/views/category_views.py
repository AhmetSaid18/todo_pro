from apps.core.views import AgencyModelViewSet
from apps.equipment.models import EquipmentCategory
from apps.equipment.serializers import CategorySerializer

class CategoryViewSet(AgencyModelViewSet):
    queryset = EquipmentCategory.objects.all()
    serializer_class = CategorySerializer
