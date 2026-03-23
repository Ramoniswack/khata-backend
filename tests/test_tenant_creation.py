#!/usr/bin/env python
"""
Test script for tenant creation API
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from tenants.serializers import TenantCreateSerializer

def test_tenant_creation():
    """Test tenant creation with serializer"""
    print("=" * 60)
    print("TESTING TENANT CREATION")
    print("=" * 60)
    
    # Test data
    test_data = {
        'name': 'Test Construction Company',
        'business_type': 'construction',
        'owner_name': 'John Doe',
        'email': 'john@test.com',
        'phone': '+977 9812345678',
        'address': 'Kathmandu, Nepal',
        'active_modules': ['inventory', 'sales', 'construction', 'accounting', 'reports']
    }
    
    print("\n1. Testing tenant creation with full data...")
    print(f"Data: {test_data}")
    
    # Delete existing tenant with same name
    Tenant.objects.filter(name=test_data['name']).delete()
    
    # Create tenant
    serializer = TenantCreateSerializer(data=test_data)
    if serializer.is_valid():
        tenant = serializer.save()
        print(f"✅ Tenant created successfully!")
        print(f"   ID: {tenant.id}")
        print(f"   Name: {tenant.name}")
        print(f"   Slug: {tenant.slug}")
        print(f"   Business Type: {tenant.business_type}")
        print(f"   Owner: {tenant.owner_name}")
        print(f"   Email: {tenant.email}")
        print(f"   Phone: {tenant.phone}")
        print(f"   Address: {tenant.address}")
        print(f"   Plan: {tenant.plan_type}")
        print(f"   Active: {tenant.is_active}")
        print(f"   Modules: {tenant.active_modules}")
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return False
    
    # Test 2: Minimal data
    print("\n2. Testing tenant creation with minimal data...")
    minimal_data = {
        'name': 'Minimal Test Company',
        'business_type': 'other',
    }
    print(f"Data: {minimal_data}")
    
    Tenant.objects.filter(name=minimal_data['name']).delete()
    
    serializer = TenantCreateSerializer(data=minimal_data)
    if serializer.is_valid():
        tenant = serializer.save()
        print(f"✅ Tenant created successfully!")
        print(f"   ID: {tenant.id}")
        print(f"   Name: {tenant.name}")
        print(f"   Slug: {tenant.slug}")
        print(f"   Default Modules: {tenant.active_modules}")
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return False
    
    # Test 3: Duplicate name
    print("\n3. Testing duplicate name validation...")
    duplicate_data = {
        'name': 'Test Construction Company',  # Already exists
        'business_type': 'construction',
    }
    print(f"Data: {duplicate_data}")
    
    serializer = TenantCreateSerializer(data=duplicate_data)
    if not serializer.is_valid():
        print(f"✅ Validation correctly failed: {serializer.errors}")
    else:
        print(f"❌ Should have failed validation for duplicate name")
        return False
    
    # Test 4: Slug generation
    print("\n4. Testing slug generation...")
    slug_test_data = {
        'name': 'ABC Construction & Hardware',
        'business_type': 'construction',
    }
    print(f"Data: {slug_test_data}")
    
    Tenant.objects.filter(name=slug_test_data['name']).delete()
    
    serializer = TenantCreateSerializer(data=slug_test_data)
    if serializer.is_valid():
        tenant = serializer.save()
        print(f"✅ Tenant created successfully!")
        print(f"   Name: {tenant.name}")
        print(f"   Slug: {tenant.slug}")
        print(f"   Expected slug format: abc-construction-hardware")
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = test_tenant_creation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
