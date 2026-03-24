import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee, LeaveType, LeaveRequest
from tenants.models import Tenant
from users.models import User

# Get first tenant and user
tenant = Tenant.objects.first()
user = User.objects.filter(tenant=tenant).first()

print(f"Tenant: {tenant.name}")
if user:
    print(f"User: {user.username}")
else:
    print("User: None found")

# Check leave types
leave_types = LeaveType.objects.filter(tenant=tenant)
print(f"\nLeave types: {leave_types.count()}")
for lt in leave_types:
    print(f"  - {lt.id}: {lt.name}")

# Check employees
employees = Employee.objects.filter(tenant=tenant, status='active')
print(f"\nActive employees: {employees.count()}")
for emp in employees:
    print(f"  - {emp.id}: {emp.name}")

if leave_types.exists() and employees.exists():
    # Try to create a leave request
    leave_type = leave_types.first()
    employee = employees.first()
    
    print(f"\nCreating leave request...")
    print(f"  Leave Type ID: {leave_type.id}")
    print(f"  Employee ID: {employee.id}")
    
    try:
        leave_request = LeaveRequest.objects.create(
            tenant=tenant,
            employee=employee,
            leave_type=leave_type,
            start_date="2024-03-25",
            end_date="2024-03-27",
            reason="Test leave request",
            status="pending"
        )
        print(f"\n✓ Leave request created successfully!")
        print(f"  ID: {leave_request.id}")
        print(f"  Days: {leave_request.days_requested}")
        
        # Clean up
        leave_request.delete()
        print(f"\n✓ Test leave request deleted")
    except Exception as e:
        print(f"\n✗ Error creating leave request: {e}")
else:
    if not leave_types.exists():
        print("\n⚠ No leave types found. Run seed_leave_types.py first.")
    if not employees.exists():
        print("\n⚠ No active employees found.")
