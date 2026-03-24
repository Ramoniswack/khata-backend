import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from hr.models import Employee, Department
from datetime import date

# Get the user you're logged in as (change this to match your login)
print("Available users:")
for i, user in enumerate(User.objects.all()[:10], 1):
    print(f"{i}. {user.username} - {user.tenant.name if user.tenant else 'No tenant'}")

print("\nEnter the username you're logged in as:")
print("(Or press Enter to use 'admin')")
username = input().strip() or 'admin'

try:
    user = User.objects.get(username=username)
    print(f"\nUser: {user.username}")
    print(f"Tenant: {user.tenant.name}")
    
    # Check if tenant already has employees
    existing_employees = Employee.objects.filter(tenant=user.tenant)
    if existing_employees.exists():
        print(f"\nTenant already has {existing_employees.count()} employee(s):")
        for emp in existing_employees:
            print(f"  - {emp.name} (Status: {emp.status})")
        
        print("\nDo you want to create another employee? (y/n)")
        if input().strip().lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Get or create a department
    dept = Department.objects.filter(tenant=user.tenant).first()
    if not dept:
        dept = Department.objects.create(
            tenant=user.tenant,
            name="General",
            description="General department"
        )
        print(f"\n✓ Created department: {dept.name}")
    else:
        print(f"\nUsing existing department: {dept.name}")
    
    # Create an employee
    emp = Employee.objects.create(
        tenant=user.tenant,
        name=f"{user.username.title()} Employee",
        email=user.email,
        phone="1234567890",
        dob=date(1990, 1, 1),
        gender="Male",
        department=dept,
        designation="Staff",
        employment_type="Full-time",
        join_date=date.today(),
        basic_salary=50000,
        status="active",
        user=user  # Link to the user account
    )
    print(f"\n✓ Created active employee: {emp.name}")
    print(f"  Linked to user: {user.username}")
    print(f"  Department: {dept.name}")
    print(f"  Status: {emp.status}")
    
    print("\n✓ Done! You can now create leave requests.")
    
except User.DoesNotExist:
    print(f"\n✗ User '{username}' not found")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
