import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee, Department
from tenants.models import Tenant

# Get first tenant
tenant = Tenant.objects.first()
print(f"Tenant: {tenant.name}")

# Check employees
employees = Employee.objects.filter(tenant=tenant)
print(f"\nTotal employees: {employees.count()}")

active_employees = employees.filter(status='active')
print(f"Active employees: {active_employees.count()}")

if employees.exists():
    print("\nAll employees:")
    for emp in employees:
        print(f"  - {emp.name} (Status: {emp.status})")
    
    # If no active employees, activate the first one
    if not active_employees.exists():
        first_emp = employees.first()
        first_emp.status = 'active'
        first_emp.save()
        print(f"\n✓ Activated employee: {first_emp.name}")
else:
    print("\n⚠ No employees found. Creating a test employee...")
    
    # Get or create a department
    dept = Department.objects.filter(tenant=tenant).first()
    if not dept:
        dept = Department.objects.create(
            tenant=tenant,
            name="General",
            description="General department"
        )
        print(f"✓ Created department: {dept.name}")
    
    # Create an employee
    emp = Employee.objects.create(
        tenant=tenant,
        name="Test Employee",
        email="test@example.com",
        phone="1234567890",
        department=dept,
        designation="Staff",
        employment_type="full_time",
        join_date="2024-01-01",
        basic_salary=50000,
        status="active"
    )
    print(f"✓ Created active employee: {emp.name}")

print("\n✓ Done! You can now create leave requests.")
