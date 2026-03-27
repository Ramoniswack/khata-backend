#!/usr/bin/env python
"""
Run this with: python manage.py shell < scripts/check_user2_simple.py
"""

from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantUser

User = get_user_model()

# Check user2@test.com
try:
    user = User.objects.get(email='user2@test.com')
    print(f"\n=== User: {user.email} ===")
    print(f"ID: {user.id}")
    print(f"Role: {user.role}")
    
    # Check tenant assignment
    tenant_users = TenantUser.objects.filter(user=user)
    print(f"\nTenant Assignments: {tenant_users.count()}")
    
    for tu in tenant_users:
        print(f"\n  Tenant: {tu.tenant.name}")
        print(f"  Tenant ID: {tu.tenant.id}")
        print(f"  Tenant Slug: {tu.tenant.slug}")
        print(f"  Role: {tu.role}")
        print(f"  Is Active: {tu.tenant.is_active}")
        
    # Check created tenants
    created_tenants = Tenant.objects.filter(created_by=user)
    print(f"\nTenants Created: {created_tenants.count()}")
    for tenant in created_tenants:
        print(f"  - {tenant.name} (slug: {tenant.slug})")
        
    # What API returns
    print(f"\n=== API Profile Response ===")
    if tenant_users.exists():
        first_tenant = tenant_users.first().tenant
        print(f"user.tenant: {first_tenant.name} (ID: {first_tenant.id}, slug: {first_tenant.slug})")
        print(f"This is why user can access dashboard!")
    else:
        print("user.tenant: None")
        print("User should NOT be able to access dashboard")
        
except User.DoesNotExist:
    print("User user2@test.com not found")
