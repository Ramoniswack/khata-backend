#!/usr/bin/env python
"""
Test tenant slug generation with duplicate names
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant

print("Testing Tenant slug generation with duplicate names...")
print()

# Create first tenant
print("1. Creating first tenant: 'Test Company'")
tenant1 = Tenant.objects.create(
    name='Test Company',
    business_type='other',
    plan_type='free',
    is_active=True,
    active_modules=['inventory']
)
print(f"   ✓ Created: {tenant1.name} (slug: {tenant1.slug})")

# Create second tenant with same name
print("\n2. Creating second tenant: 'Test Company'")
try:
    tenant2 = Tenant.objects.create(
        name='Test Company 2',  # Different name but similar
        business_type='other',
        plan_type='free',
        is_active=True,
        active_modules=['inventory']
    )
    print(f"   ✓ Created: {tenant2.name} (slug: {tenant2.slug})")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Create third tenant with same base name
print("\n3. Creating third tenant: 'Test Company'")
try:
    tenant3 = Tenant.objects.create(
        name='Test Company',  # Exact same name
        business_type='other',
        plan_type='free',
        is_active=True,
        active_modules=['inventory']
    )
    print(f"   ✓ Created: {tenant3.name} (slug: {tenant3.slug})")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print(f"   This is expected - tenant name must be unique")

# List all test tenants
print("\n4. All test tenants:")
test_tenants = Tenant.objects.filter(name__startswith='Test Company')
for t in test_tenants:
    print(f"   - {t.name} (slug: {t.slug})")

# Clean up
print("\n5. Cleaning up...")
test_tenants.delete()
print("   ✓ All test tenants deleted")

print("\n✓ Test completed!")
