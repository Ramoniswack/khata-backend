#!/usr/bin/env python
"""
Check for managers and create some if needed
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()


def check_and_create_managers():
    print("=" * 60)
    print("Check and Create Managers")
    print("=" * 60)
    
    # Get all tenants
    tenants = Tenant.objects.all()
    print(f"\nFound {tenants.count()} tenants")
    
    for tenant in tenants:
        print(f"\n{'=' * 60}")
        print(f"Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"{'=' * 60}")
        
        # Check for managers in this tenant
        managers = User.objects.filter(tenant=tenant, role='manager')
        print(f"Managers found: {managers.count()}")
        
        if managers.count() > 0:
            print("\nExisting managers:")
            for manager in managers:
                print(f"  - {manager.username} ({manager.first_name} {manager.last_name}) - {manager.email}")
        else:
            print("\n⚠️  No managers found for this tenant!")
            
            # Check if there are any users with admin role
            admins = User.objects.filter(tenant=tenant, role='admin')
            
            if admins.count() > 0:
                print(f"\nFound {admins.count()} admin(s). Creating a manager user...")
                
                # Create a manager user
                manager_username = f"manager_{tenant.slug}"
                manager_email = f"manager@{tenant.slug}.com"
                
                # Check if user already exists
                if User.objects.filter(username=manager_username).exists():
                    print(f"✅ Manager user '{manager_username}' already exists")
                else:
                    manager = User.objects.create_user(
                        username=manager_username,
                        email=manager_email,
                        password='manager123',  # Default password
                        first_name='Site',
                        last_name='Manager',
                        role='manager',
                        tenant=tenant
                    )
                    print(f"✅ Created manager: {manager.username}")
                    print(f"   Email: {manager.email}")
                    print(f"   Password: manager123")
                    print(f"   Name: {manager.first_name} {manager.last_name}")
            else:
                print("⚠️  No admin users found either. Cannot create manager.")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    # Count total managers across all tenants
    total_managers = User.objects.filter(role='manager').count()
    print(f"\nTotal managers in system: {total_managers}")
    
    if total_managers == 0:
        print("\n⚠️  WARNING: No managers found in the system!")
        print("Construction sites require managers to be assigned.")
        print("\nTo create a manager manually:")
        print("1. Go to Django admin: http://localhost:8000/admin/")
        print("2. Navigate to Users")
        print("3. Create a new user with role='manager'")
        print("\nOr run this script again after creating an admin user.")
    else:
        print("\n✅ Managers are available for construction site assignment")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    check_and_create_managers()
