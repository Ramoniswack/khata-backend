#!/usr/bin/env python
"""
Seed Leave Types for HR Module
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import LeaveType
from tenants.models import Tenant

def seed_leave_types():
    print("=" * 60)
    print("SEEDING LEAVE TYPES")
    print("=" * 60)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Please create a tenant first.")
        return
    
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Define leave types
    leave_types_data = [
        {
            'name': 'Annual Leave',
            'days_allowed': 15,
            'description': 'Paid annual leave for employees',
            'is_paid': True
        },
        {
            'name': 'Sick Leave',
            'days_allowed': 10,
            'description': 'Leave for medical reasons',
            'is_paid': True
        },
        {
            'name': 'Casual Leave',
            'days_allowed': 7,
            'description': 'Short-term casual leave',
            'is_paid': True
        },
        {
            'name': 'Maternity Leave',
            'days_allowed': 90,
            'description': 'Maternity leave for female employees',
            'is_paid': True
        },
        {
            'name': 'Paternity Leave',
            'days_allowed': 15,
            'description': 'Paternity leave for male employees',
            'is_paid': True
        },
        {
            'name': 'Unpaid Leave',
            'days_allowed': 30,
            'description': 'Leave without pay',
            'is_paid': False
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for lt_data in leave_types_data:
        leave_type, created = LeaveType.objects.update_or_create(
            tenant=tenant,
            name=lt_data['name'],
            defaults={
                'days_allowed': lt_data['days_allowed'],
                'description': lt_data['description'],
                'is_paid': lt_data['is_paid']
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {leave_type.name} ({leave_type.days_allowed} days)")
        else:
            updated_count += 1
            print(f"✓ Updated: {leave_type.name} ({leave_type.days_allowed} days)")
    
    print(f"\n✓ Created {created_count} new leave types")
    print(f"✓ Updated {updated_count} existing leave types")
    
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    seed_leave_types()
