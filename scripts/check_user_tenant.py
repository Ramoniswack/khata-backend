import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from hr.models import Employee
from tenants.models import Tenant

print("=== Checking User and Tenant Context ===\n")

# List all users
users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users:
    print(f"\nUser: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Tenant: {user.tenant.name if user.tenant else 'None'}")
    print(f"  Is superuser: {user.is_superuser}")
    
    # Check if user has employee profile
    if hasattr(user, 'employee_profile') and user.employee_profile:
        emp = user.employee_profile
        print(f"  Employee Profile: {emp.name} (Status: {emp.status})")
    else:
        print(f"  Employee Profile: None")

# List all tenants and their employees
print("\n=== Tenants and Employees ===\n")
for tenant in Tenant.objects.all():
    print(f"Tenant: {tenant.name}")
    employees = Employee.objects.filter(tenant=tenant)
    print(f"  Total employees: {employees.count()}")
    print(f"  Active employees: {employees.filter(status='active').count()}")
    
    for emp in employees:
        print(f"    - {emp.name} (Status: {emp.status}, User: {emp.user.username if emp.user else 'None'})")
