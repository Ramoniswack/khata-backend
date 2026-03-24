#!/usr/bin/env python
"""Seed payroll data for testing"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Payroll, Employee
from tenants.models import Tenant
from decimal import Decimal
from django.utils import timezone

def seed_payroll():
    """Seed payroll data"""
    print("🌱 Seeding payroll data...")
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found")
        return
    
    print(f"✅ Using tenant: {tenant.name}")
    
    # Get active employees
    employees = Employee.objects.filter(tenant=tenant, status='active')
    if not employees.exists():
        print("❌ No active employees found")
        return
    
    print(f"✅ Found {employees.count()} active employees")
    
    # Create payroll for multiple months
    months = [
        ("Shrawan", 2081),
        ("Bhadra", 2081),
        ("Ashwin", 2081),
    ]
    
    created_count = 0
    for month, year in months:
        for employee in employees:
            basic_salary = employee.basic_salary
            allowances = basic_salary * Decimal('0.15')
            gross_salary = basic_salary + allowances
            deductions = basic_salary * Decimal('0.15')
            net_salary = gross_salary - deductions
            
            payroll, created = Payroll.objects.get_or_create(
                tenant=tenant,
                employee=employee,
                month=month,
                year=year,
                defaults={
                    'basic_salary': basic_salary,
                    'allowances': allowances,
                    'gross_salary': gross_salary,
                    'deductions': deductions,
                    'net_salary': net_salary,
                    'status': 'processed',
                    'processed_date': timezone.now()
                }
            )
            
            if created:
                created_count += 1
                print(f"   ✅ Created payroll: {employee.name} - {month} {year}")
    
    print(f"\n✅ Created {created_count} payroll records")

if __name__ == "__main__":
    seed_payroll()
