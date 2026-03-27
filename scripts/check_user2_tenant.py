import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantUser

User = get_user_model()

# Check user2@test.com
try:
    user = User.objects.get(email='user2@test.com')
    print(f"\n=== User: {user.email} ===")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Role: {user.role}")
    
    # Check tenant assignment
    tenant_users = TenantUser.objects.filter(user=user)
    print(f"\n=== Tenant Assignments ({tenant_users.count()}) ===")
    
    for tu in tenant_users:
        print(f"\nTenant: {tu.tenant.name}")
        print(f"  - Tenant ID: {tu.tenant.id}")
        print(f"  - Tenant Slug: {tu.tenant.slug}")
        print(f"  - Role in Tenant: {tu.role}")
        print(f"  - Is Active: {tu.tenant.is_active}")
        print(f"  - Created By: {tu.tenant.created_by.email if tu.tenant.created_by else 'None'}")
        
    # Check what tenants this user created
    created_tenants = Tenant.objects.filter(created_by=user)
    print(f"\n=== Tenants Created by User ({created_tenants.count()}) ===")
    for tenant in created_tenants:
        print(f"\nTenant: {tenant.name}")
        print(f"  - ID: {tenant.id}")
        print(f"  - Slug: {tenant.slug}")
        print(f"  - Is Active: {tenant.is_active}")
        
    # Check what the API would return
    print(f"\n=== API Response Simulation ===")
    # This simulates what /auth/profile/ returns
    if tenant_users.exists():
        first_tenant = tenant_users.first().tenant
        print(f"user.tenant would be: {first_tenant.name} (ID: {first_tenant.id})")
    else:
        print("user.tenant would be: None")
        
except User.DoesNotExist:
    print("User user2@test.com not found")
