from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

# Check user2@test.com
try:
    user = User.objects.get(email='user2@test.com')
    print(f"\n=== User: {user.email} ===")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Tenant: {user.tenant}")
    
    if user.tenant:
        print(f"\n=== Tenant Details ===")
        print(f"Tenant Name: {user.tenant.name}")
        print(f"Tenant ID: {user.tenant.id}")
        print(f"Tenant Slug: {user.tenant.slug}")
        print(f"Is Active: {user.tenant.is_active}")
        print(f"Created By: {user.tenant.created_by.email if user.tenant.created_by else 'None'}")
        print(f"Created from Registration: {user.tenant.created_from_registration}")
        print(f"\nThis is why user can access dashboard!")
        print(f"Solution: Set user.tenant = None to block dashboard access")
    else:
        print(f"\nTenant: None")
        print(f"User should NOT be able to access dashboard")
        
    # Check tenants created by this user
    created_tenants = Tenant.objects.filter(created_by=user)
    print(f"\n=== Tenants Created by User: {created_tenants.count()} ===")
    for tenant in created_tenants:
        print(f"  - {tenant.name} (slug: {tenant.slug}, active: {tenant.is_active})")
        
    # Check all tenants where this user is a member
    all_user_tenants = Tenant.objects.filter(users=user)
    print(f"\n=== All Tenants with User as Member: {all_user_tenants.count()} ===")
    for tenant in all_user_tenants:
        print(f"  - {tenant.name} (slug: {tenant.slug})")
        
except User.DoesNotExist:
    print("User user2@test.com not found")
