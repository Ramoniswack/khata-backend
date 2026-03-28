#!/usr/bin/env python
"""
Initialize permissions for tenants that don't have any permissions set up.
This script should be run after the permissions system is deployed.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from users.permission_models import RolePermission, initialize_tenant_permissions


def main():
    print("=" * 60)
    print("Initialize Missing Permissions Script")
    print("=" * 60)
    
    # Get all active tenants
    tenants = Tenant.objects.filter(is_active=True)
    print(f"\nFound {tenants.count()} active tenants")
    
    tenants_without_permissions = []
    tenants_with_permissions = []
    
    for tenant in tenants:
        # Check if tenant has any permissions
        perm_count = RolePermission.objects.filter(tenant=tenant).count()
        
        if perm_count == 0:
            tenants_without_permissions.append(tenant)
            print(f"\n❌ Tenant '{tenant.name}' (ID: {tenant.id}) has NO permissions")
        else:
            tenants_with_permissions.append(tenant)
            print(f"\n✅ Tenant '{tenant.name}' (ID: {tenant.id}) has {perm_count} permissions")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  - Tenants with permissions: {len(tenants_with_permissions)}")
    print(f"  - Tenants without permissions: {len(tenants_without_permissions)}")
    print("=" * 60)
    
    if not tenants_without_permissions:
        print("\n✅ All tenants have permissions initialized!")
        return
    
    print(f"\n⚠️  Found {len(tenants_without_permissions)} tenants without permissions")
    print("\nInitializing permissions for these tenants...")
    
    for tenant in tenants_without_permissions:
        print(f"\n  Initializing permissions for '{tenant.name}'...")
        try:
            initialize_tenant_permissions(tenant)
            perm_count = RolePermission.objects.filter(tenant=tenant).count()
            print(f"  ✅ Created {perm_count} permissions for '{tenant.name}'")
        except Exception as e:
            print(f"  ❌ Error initializing permissions for '{tenant.name}': {e}")
    
    print("\n" + "=" * 60)
    print("✅ Permissions initialization complete!")
    print("=" * 60)
    
    # Verify all tenants now have permissions
    print("\nVerifying...")
    for tenant in Tenant.objects.filter(is_active=True):
        perm_count = RolePermission.objects.filter(tenant=tenant).count()
        if perm_count == 0:
            print(f"  ❌ Tenant '{tenant.name}' still has no permissions!")
        else:
            print(f"  ✅ Tenant '{tenant.name}' has {perm_count} permissions")


if __name__ == '__main__':
    main()
