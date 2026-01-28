from apps.core.models import BaseModel
from apps.agencies.models import Agency, AgencyRole, AgencyAwareModel, Client
from apps.users.models import User, AgencyMembership, Notification, AuditLog
from apps.projects.models import Project, Location, File, Expense, ExpenseCategory, ShootingDay, CallSheet
from apps.tasks.models import Task
from apps.equipment.models import Equipment, EquipmentCategory, EquipmentReservation

# Attempt to import FileTransfer if available (it might be missing)
try:
    from apps.projects.models import FileTransfer
except ImportError:
    pass