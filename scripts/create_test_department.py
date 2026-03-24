#!/usr/bin/env python
"""
Create a test department for HR module testing
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Department
from tenants.models import Tenant


def create_test_department():
    print("Creating test department...")
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("ERROR: No tenant found. Please create a tenant first.")
        return
    
    print(f"Using tenant: {tenant.name}")
    
    # Create departments
    departments = [
        {'name': 'Sales Department', 'description': 'Handles all sales operations'},
        {'name': 'IT Department', 'description': 'Information Technology'},
        {'name': 'HR Department', 'description': 'Human Resources'},
        {'name': 'Finance Department', 'description': 'Financial operations'},
    ]
    
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            tenant=tenant,
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        status = "Created" if created else "Already exists"
        print(f"  {status}: {dept.name}")
    
    print("\nDepartments ready for testing!")
    print(f"Total departments: {Department.objects.filter(tenant=tenant).count()}")


if __name__ == '__main__':
    create_test_department()
