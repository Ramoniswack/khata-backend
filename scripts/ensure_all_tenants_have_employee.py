import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from hr.models import Employee, Department
from tenants.models import Tenant
from datetime import date

print("=== Ensuring All Tenants Have At Least One Active Employee ===\n")

tenants_fixed = 0
tenants_skipped = 0

for tenant in Tenant.objects.all():
    # Check if tenant has active employees
    active_employees = Employee.objects.filter(tenant=tenant, status='active')
    
    if active_employees.exists():
        print(f"✓ {tenant.name}: Already has {active_employees.count()} active employee(s)")
        tenants_skipped += 1
        continue
    
    print(f"\n→ {tenant.name}: No active employees, creating one...")
    
    try:
        # Get or create a department
        dept = Department.objects.filter(tenant=tenant).first()
        if not dept:
            dept = Department.objects.create(
                tenant=tenant,
                name="General",
                description="General department"
            )
            print(f"  ✓ Created department: {dept.name}")
        
        # Get a user from this tenant to link to
        user = User.objects.filter(tenant=tenant).first()
        
        # Create an employee
        emp = Employee.objects.create(
            tenant=tenant,
            name=f"Default Employee",
            email=user.email if user else f"employee@{tenant.slug}.com",
            phone="1234567890",
            dob=date(1990, 1, 1),
            gender="Male",
            department=dept,
            designation="Staff",
            employment_type="Full-time",
            join_date=date.today(),
            basic_salary=50000,
            status="active",
            user=user  # Link to user if available
        )
        print(f"  ✓ Created employee: {emp.name}")
        if user:
            print(f"  ✓ Linked to user: {user.username}")
        
        tenants_fixed += 1
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n=== Summary ===")
print(f"Tenants with employees: {tenants_skipped}")
print(f"Tenants fixed: {tenants_fixed}")
print(f"\n✓ Done! All tenants now have at least one active employee.")
