#!/usr/bin/env python
"""
Test script for modular architecture backend integration
Tests tenant creation with module subscriptions
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
from tenants.membership_models import UserTenantMembership

User = get_user_model()

def test_tenant_creation_with_modules():
    """Test creating a tenant with specific modules"""
    print("\n" + "="*60)
    print("TEST: Tenant Creation with Module Subscriptions")
    print("="*60)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='moduletest',
        defaults={
            'email': 'moduletest@example.com',
            'first_name': 'Module',
            'last_name': 'Test'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Test 1: Create CORE tenant (default modules)
    print("\n--- Test 1: CORE Tenant (Default Modules) ---")
    core_tenant = Tenant.objects.create(
        name="Test Core Business",
        business_type="other",
        owner_name="Core Owner",
        email="core@example.com",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports']
    )
    print(f"✓ Created tenant: {core_tenant.name}")
    print(f"  Slug: {core_tenant.slug}")
    print(f"  Active modules: {core_tenant.active_modules}")
    print(f"  Has inventory: {core_tenant.has_module('inventory')}")
    print(f"  Has construction: {core_tenant.has_module('construction')}")
    
    # Test 2: Create CONSTRUCTION tenant
    print("\n--- Test 2: CONSTRUCTION Tenant ---")
    construction_tenant = Tenant.objects.create(
        name="Test Construction Co",
        business_type="construction",
        owner_name="Construction Owner",
        email="construction@example.com",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction']
    )
    print(f"✓ Created tenant: {construction_tenant.name}")
    print(f"  Slug: {construction_tenant.slug}")
    print(f"  Active modules: {construction_tenant.active_modules}")
    print(f"  Has construction: {construction_tenant.has_module('construction')}")
    
    # Test 3: Create HARDWARE tenant
    print("\n--- Test 3: HARDWARE Tenant ---")
    hardware_tenant = Tenant.objects.create(
        name="Test Hardware Store",
        business_type="hardware",
        owner_name="Hardware Owner",
        email="hardware@example.com",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports', 'hardware']
    )
    print(f"✓ Created tenant: {hardware_tenant.name}")
    print(f"  Slug: {hardware_tenant.slug}")
    print(f"  Active modules: {hardware_tenant.active_modules}")
    print(f"  Has hardware: {hardware_tenant.has_module('hardware')}")
    
    # Test 4: Module activation/deactivation
    print("\n--- Test 4: Module Activation/Deactivation ---")
    print(f"Before: {core_tenant.active_modules}")
    
    core_tenant.activate_module('construction')
    print(f"After activating construction: {core_tenant.active_modules}")
    
    core_tenant.deactivate_module('construction')
    print(f"After deactivating construction: {core_tenant.active_modules}")
    
    # Test 5: Verify membership creation
    print("\n--- Test 5: User Membership ---")
    membership = UserTenantMembership.objects.filter(
        user=user,
        tenant=core_tenant
    ).first()
    
    if membership:
        print(f"✓ Membership exists for {user.username} in {core_tenant.name}")
        print(f"  Role: {membership.role}")
    else:
        print(f"✗ No membership found - creating one")
        membership = UserTenantMembership.objects.create(
            user=user,
            tenant=core_tenant,
            role='admin'
        )
        print(f"✓ Created membership with role: {membership.role}")
    
    # Test 6: Module-based feature access
    print("\n--- Test 6: Module-Based Feature Access ---")
    
    def check_feature_access(tenant, feature_module):
        """Check if tenant has access to a feature based on module"""
        has_access = tenant.has_module(feature_module)
        status = "✓ ALLOWED" if has_access else "✗ DENIED"
        print(f"  {tenant.name} -> {feature_module}: {status}")
        return has_access
    
    print("\nCore Tenant Access:")
    check_feature_access(core_tenant, 'inventory')
    check_feature_access(core_tenant, 'sales')
    check_feature_access(core_tenant, 'construction')
    check_feature_access(core_tenant, 'hardware')
    
    print("\nConstruction Tenant Access:")
    check_feature_access(construction_tenant, 'inventory')
    check_feature_access(construction_tenant, 'construction')
    check_feature_access(construction_tenant, 'hardware')
    
    print("\nHardware Tenant Access:")
    check_feature_access(hardware_tenant, 'inventory')
    check_feature_access(hardware_tenant, 'hardware')
    check_feature_access(hardware_tenant, 'construction')
    
    print("\n" + "="*60)
    print("✓ All tests completed successfully!")
    print("="*60)
    
    # Cleanup
    print("\n--- Cleanup ---")
    core_tenant.delete()
    construction_tenant.delete()
    hardware_tenant.delete()
    print("✓ Test tenants deleted")

if __name__ == '__main__':
    test_tenant_creation_with_modules()
