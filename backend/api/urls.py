from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.project import ProjectViewSet
from api.views.task import TaskViewSet
from api.views.equipment import EquipmentViewSet, ReservationViewSet, CategoryViewSet
from api.views.client import ClientViewSet
from api.views.location import LocationViewSet
from api.views.file import FileViewSet
from api.views.finance_schedule import ExpenseViewSet, ShootingDayViewSet, CallSheetViewSet
from api.views.user import UserViewSet
from api.views.transfer import TransferViewSet
from api.views.notification import NotificationViewSet
from api.views.dashboard import DashboardStatsView
from api.views.health import health_check
from api.views import auth

router = DefaultRouter()
# User & Auth
router.register(r'users', UserViewSet, basename='user')

# Notifications
router.register(r'notifications', NotificationViewSet, basename='notification')

# WeTransfer Module
router.register(r'transfers', TransferViewSet)

# Projects Domain
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'files', FileViewSet)

# Finance & Schedule
router.register(r'expenses', ExpenseViewSet)
router.register(r'shooting-days', ShootingDayViewSet)
router.register(r'call-sheets', CallSheetViewSet)

# Inventory Domain
router.register(r'items', EquipmentViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    # System
    path('health/', health_check, name='health-check'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Authentication
    path('auth/register/', auth.register, name='auth-register'),
    path('auth/login/', auth.login, name='auth-login'),
    path('auth/logout/', auth.logout, name='auth-logout'),
    path('auth/refresh/', auth.refresh_token, name='auth-refresh'),
    path('auth/switch-agency/', auth.switch_agency, name='auth-switch-agency'),
    path('auth/my-agencies/', auth.my_agencies, name='auth-my-agencies'),
    
    # Router endpoints
    path('', include(router.urls)),
]
