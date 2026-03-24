#!/usr/bin/env python
"""Seed HR data for Demo Company tenant"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Department, Employee, Attendance
from tenants.models import Tenant
from decimal import Decimal
from datetime import datetime, timedelta
import random

def seed_data():
    """Seed HR test data for Demo Company"""
    print("🌱 Seeding HR data for Demo Company...")
    
    # Get Demo Company tenant
    tenant = Tenant.objects.filter(name="Demo Company").first()
    if not tenant:
        print("❌ Demo Company tenant not found")
        return
    
    print(f"✅ Using tenant: {tenant.name}")
    
    # Create departments
    departments_data = [
        ("Operations", "Operations and logistics"),
        ("Sales", "Sales and marketing"),
        ("Finance", "Finance and accounting"),
        ("IT", "Information technology"),
        ("Admin", "Administration"),
    ]
    
    departments = []
    for name, desc in departments_data:
        dept, created = Department.objects.get_or_create(
            tenant=tenant,
            name=name,
            defaults={'description': desc}
        )
        departments.append(dept)
        if created:
            print(f"   ✅ Created department: {name}")
    
    # Create employees
    employees_data = [
        ("John Doe", "Manager", 80000, "Full-time"),
        ("Jane Smith", "Developer", 70000, "Full-time"),
        ("Bob Johnson", "Sales Rep", 60000, "Full-time"),
        ("Alice Brown", "Accountant", 65000, "Full-time"),
        ("Charlie Wilson", "IT Support", 55000, "Part-time"),
        ("Diana Davis", "Admin Assistant", 50000, "Contract"),
        ("Eve Martinez", "Junior Developer", 45000, "Probation"),
        ("Frank Garcia", "Sales Manager", 75000, "Full-time"),
    ]
    
    genders = ['Male', 'Female']
    employees = []
    
    for i, (name, designation, salary, emp_type) in enumerate(employees_data):
        dept = departments[i % len(departments)]
        
        emp, created = Employee.objects.get_or_create(
            tenant=tenant,
            email=f"{name.lower().replace(' ', '.')}@democompany.com",
            defaults={
                'name': name,
                'dob': datetime(1990 + i, 1, 1).date(),
                'gender': random.choice(genders),
                'phone': f"+977-98{20000000 + i}",
                'department': dept,
                'designation': designation,
                'employment_type': emp_type,
                'join_date': datetime(2020 + i % 3, 1, 1).date(),
                'basic_salary': Decimal(str(salary)),
                'status': 'active'
            }
        )
        employees.append(emp)
        if created:
            print(f"   ✅ Created employee: {name}")
    
    # Create attendance records for last 7 days
    today = datetime.now().date()
    statuses = ['present', 'present', 'present', 'present', 'late', 'absent']
    
    for i in range(7):
        date = today - timedelta(days=i)
        for employee in employees:
            status = random.choice(statuses)
            
            Attendance.objects.get_or_create(
                tenant=tenant,
                employee=employee,
                date=date,
                defaults={
                    'status': status,
                    'check_in': datetime.strptime('09:00', '%H:%M').time() if status != 'absent' else None,
                    'check_out': datetime.strptime('17:00', '%H:%M').time() if status != 'absent' else None,
                }
            )
    
    print(f"\n✅ Seeded {len(employees)} employees across {len(departments)} departments for Demo Company")
    print(f"✅ Created attendance records for last 7 days")

if __name__ == "__main__":
    seed_data()
