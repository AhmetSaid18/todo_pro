from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, ReservationViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'items', EquipmentViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [path('', include(router.urls))]
