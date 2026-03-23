"""
Test to understand the category tenant filtering issue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Category, UnitOfMeasure
from tenants.models import Tenant
from tenants.middleware import set_current_tenant

User = get_user_model()

print("="*60)
print("CATEGORY TENANT FILTERING TEST")
print("="*60)

# Get two different tenants
tenants = list(Tenant.objects.all()[:2])
if len(tenants) < 2:
    print("ERROR: Need at least 2 tenants for this test")
    exit(1)

tenant1 = tenants[0]
tenant2 = tenants[1]

print(f"\nTenant 1: {tenant1.name} (ID: {tenant1.id})")
print(f"Tenant 2: {tenant2.name} (ID: {tenant2.id})")

# Get categories for each tenant
print("\n" + "="*60)
print("WITHOUT TENANT CONTEXT (should see all)")
print("="*60)
set_current_tenant(None)
all_categories = Category.objects.all()
print(f"Total categories: {all_categories.count()}")

print("\n" + "="*60)
print(f"WITH TENANT 1 CONTEXT: {tenant1.name}")
print("="*60)
set_current_tenant(tenant1)
tenant1_categories = Category.objects.all()
print(f"Categories visible: {tenant1_categories.count()}")
for cat in tenant1_categories[:3]:
    print(f"  - {cat.name} (ID: {cat.id}, Tenant: {cat.tenant.name})")

# Try to get a category from tenant 2 while in tenant 1 context
if tenant1_categories.exists():
    tenant1_cat_id = tenant1_categories.first().id
    print(f"\nTrying to get category ID {tenant1_cat_id} (belongs to tenant 1):")
    try:
        cat = Category.objects.get(id=tenant1_cat_id)
        print(f"  ✓ Found: {cat.name} (Tenant: {cat.tenant.name})")
    except Category.DoesNotExist:
        print(f"  ✗ Not found (filtered out)")

print("\n" + "="*60)
print(f"WITH TENANT 2 CONTEXT: {tenant2.name}")
print("="*60)
set_current_tenant(tenant2)
tenant2_categories = Category.objects.all()
print(f"Categories visible: {tenant2_categories.count()}")
for cat in tenant2_categories[:3]:
    print(f"  - {cat.name} (ID: {cat.id}, Tenant: {cat.tenant.name})")

# Try to get a category from tenant 1 while in tenant 2 context
if tenant1_categories.exists():
    tenant1_cat_id = tenant1_categories.first().id
    print(f"\nTrying to get category ID {tenant1_cat_id} (belongs to tenant 1):")
    try:
        cat = Category.objects.get(id=tenant1_cat_id)
        print(f"  ✗ SECURITY ISSUE: Found {cat.name} from different tenant!")
        print(f"     Category tenant: {cat.tenant.name}")
        print(f"     Current tenant: {tenant2.name}")
    except Category.DoesNotExist:
        print(f"  ✓ Correctly filtered out (tenant isolation working)")

print("\n" + "="*60)
print("TESTING CATEGORY LOOKUP IN VIEW CONTEXT")
print("="*60)

# Simulate what happens in the view
user1 = User.objects.filter(tenant=tenant1).first()
if user1:
    print(f"\nUser: {user1.username} (Tenant: {user1.tenant.name})")
    set_current_tenant(user1.tenant)
    
    # Get a category ID from tenant 1
    cat = Category.objects.first()
    if cat:
        print(f"Selected category: {cat.name} (ID: {cat.id})")
        
        # This is what the view does
        try:
            lookup_cat = Category.objects.get(id=cat.id)
            print(f"✓ Lookup successful: {lookup_cat.name}")
            print(f"  Category tenant: {lookup_cat.tenant.name}")
            print(f"  User tenant: {user1.tenant.name}")
            print(f"  Match: {lookup_cat.tenant == user1.tenant}")
        except Category.DoesNotExist:
            print(f"✗ Lookup failed: Category not found")

set_current_tenant(None)
print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
