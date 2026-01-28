
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import User, Agency, AgencyMembership, AgencyRole

def create_initial_user():
    email = "admin@todo.com"
    password = "password123"
    agency_name = "Todo Agency"

    if User.objects.filter(email=email).exists():
        print(f"User {email} already exists")
        return

    # Create Agency
    agency = Agency.objects.create(
        name=agency_name,
        slug="todo-agency",
        plan="pro",
        is_active=True
    )
    print(f"Agency created: {agency.name}")

    # Create User
    user = User.objects.create_user(
        username="admin",
        email=email,
        password=password,
        first_name="Admin",
        last_name="User",
        current_agency=agency
    )
    print(f"User created: {user.email}")

    # Create Role (Owner)
    owner_role = AgencyRole.objects.create(
        agency=agency,
        name='Owner',
        can_manage_projects=True,
        can_manage_team=True,
        can_manage_equipment=True,
        can_view_finance=True
    )
    
    # Membership
    AgencyMembership.objects.create(
        user=user,
        agency=agency,
        role=owner_role,
        is_owner=True,
        is_active=True
    )
    print("Membership created")

if __name__ == '__main__':
    create_initial_user()
