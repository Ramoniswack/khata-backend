#!/usr/bin/env python
"""
Test script for HR module endpoints
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Department, Employee
from tenants.models import Tenant
from users.models import User
from datetime import date
from decimal import Decimal


def test_hr_module():
    print("=" * 60)
    print("HR MODULE TEST")
    print("=" * 60)
    
    # Get or create test tenant
    tenant, _ = Tenant.objects.get_or_create(
        name="Test Hardware Store",
        defaults={
            'business_type': 'hardware',
            'active_modules': ['hr', 'inventory', 'sales'],
            'is_active': True
        }
    )
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Create test department
    dept, created = Department.objects.get_or_create(
        tenant=tenant,
        name="Sales Department",
        defaults={
            'description': 'Handles all sales operations'
        }
    )
    print(f"\n✓ {'Created' if created else 'Found'} department: {dept.name}")
    
    # Create test employee
    employee, created = Employee.objects.get_or_create(
        tenant=tenant,
        email="john.doe@test.com",
        defaults={
            'name': 'John Doe',
            'dob': date(1990, 1, 15),
            'gender': 'Male',
            'phone': '9841234567',
            'department': dept,
            'designation': 'Sales Manager',
            'employment_type': 'Full-time',
            'join_date': date(2024, 1, 1),
            'basic_salary': Decimal('50000.00'),
            'status': 'active'
        }
    )
    print(f"\n✓ {'Created' if created else 'Found'} employee: {employee.name}")
    print(f"  - Department: {employee.department.name}")
    print(f"  - Designation: {employee.designation}")
    print(f"  - Basic Salary: Rs. {employee.basic_salary}")
    print(f"  - PF (Employee): Rs. {employee.pf_employee}")
    print(f"  - PF (Employer): Rs. {employee.pf_employer}")
    print(f"  - Total PF: Rs. {employee.total_pf}")
    print(f"  - Gross Salary: Rs. {employee.gross_salary}")
    
    # Test queries
    print(f"\n✓ Total departments: {Department.objects.filter(tenant=tenant).count()}")
    print(f"✓ Total employees: {Employee.objects.filter(tenant=tenant).count()}")
    print(f"✓ Active employees: {Employee.objects.filter(tenant=tenant, status='active').count()}")
    
    print("\n" + "=" * 60)
    print("HR MODULE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == '__main__':
    test_hr_module()
