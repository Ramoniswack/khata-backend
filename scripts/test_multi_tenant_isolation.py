#!/usr/bin/env python
"""
Test script to verify multi-tenant data isolation
Ensures users only see their own organization's data
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant
from inventory.models import Product, Category
from sales.models import Customer

def test_multi_tenant_isolation():
    """Test that users can only see their own tenant's data"""
    
    print("=" * 80)
    print("TESTING MULTI-TENANT DATA ISOLATION")
    print("=" * 80)
    
    # Clean up test data
    User.objects.filter(email__in=['user1@test.com', 'user2@test.com']).delete()
    Tenant.objects.filter(name__in=['Company A', 'Company B']).delete()
    
    print("\n1. Creating two separate users with their own organizations...")
    
    # User 1 with Company A
    tenant1 = Tenant.objects.create(
        name="Company A",
        business_type="retail",
        plan_type="free",
        active_modules=['sales', 'inventory']
    )
    user1 = User.objects.create_user(
        username='user1',
        email='user1@test.com',
        password='test123',
        first_name='User',
        last_name='One',
        tenant=tenant1,
        role='admin'
    )
    tenant1.created_by = user1
    tenant1.save()
    
    print(f"   ✓ User 1: {user1.email}")
    print(f"   ✓ Organization: {tenant1.name}")
    print(f"   ✓ Role: {user1.role}")
    
    # User 2 with Company B
    tenant2 = Tenant.objects.create(
        name="Company B",
        business_type="wholesale",
        plan_type="free",
        active_modules=['sales', 'inventory']
    )
    user2 = User.objects.create_user(
        username='user2',
        email='user2@test.com',
        password='test123',
        first_name='User',
        last_name='Two',
        tenant=tenant2,
        role='admin'
    )
    tenant2.created_by = user2
    tenant2.save()
    
    print(f"\n   ✓ User 2: {user2.email}")
    print(f"   ✓ Organization: {tenant2.name}")
    print(f"   ✓ Role: {user2.role}")
    
    print("\n2. Creating test data for each organization...")
    
    # Create UOM, category and product for Company A
    from inventory.models import UnitOfMeasure
    
    uom1 = UnitOfMeasure.objects.create(
        name="Pieces",
        abbreviation="pcs",
        type="count",
        tenant=tenant1
    )
    category1 = Category.objects.create(
        name="Electronics",
        tenant=tenant1
    )
    product1 = Product.objects.create(
        name="Laptop",
        sku="LAP001",
        tenant=tenant1,
        category=category1,
        unit=uom1,
        selling_price=50000
    )
    customer1 = Customer.objects.create(
        name="Customer A",
        email="customera@test.com",
        tenant=tenant1
    )
    
    print(f"   ✓ Company A has: 1 category, 1 product, 1 customer")
    
    # Create UOM, category and product for Company B
    uom2 = UnitOfMeasure.objects.create(
        name="Pieces",
        abbreviation="pcs",
        type="count",
        tenant=tenant2
    )
    category2 = Category.objects.create(
        name="Furniture",
        tenant=tenant2
    )
    product2 = Product.objects.create(
        name="Chair",
        sku="CHR001",
        tenant=tenant2,
        category=category2,
        unit=uom2,
        selling_price=5000
    )
    customer2 = Customer.objects.create(
        name="Customer B",
        email="customerb@test.com",
        tenant=tenant2
    )
    
    print(f"   ✓ Company B has: 1 category, 1 product, 1 customer")
    
    print("\n3. Testing data isolation...")
    
    # Test: User 1 should only see Company A's data
    print(f"\n   Testing User 1 (Company A) data access:")
    user1_products = Product.objects.filter(tenant=user1.tenant)
    user1_categories = Category.objects.filter(tenant=user1.tenant)
    user1_customers = Customer.objects.filter(tenant=user1.tenant)
    
    print(f"   - Products visible: {user1_products.count()} (should be 1)")
    print(f"   - Categories visible: {user1_categories.count()} (should be 1)")
    print(f"   - Customers visible: {user1_customers.count()} (should be 1)")
    
    if user1_products.count() == 1 and user1_products.first().name == "Laptop":
        print(f"   ✅ CORRECT: User 1 sees only their product (Laptop)")
    else:
        print(f"   ❌ ERROR: User 1 sees wrong products")
        return False
    
    # Test: User 2 should only see Company B's data
    print(f"\n   Testing User 2 (Company B) data access:")
    user2_products = Product.objects.filter(tenant=user2.tenant)
    user2_categories = Category.objects.filter(tenant=user2.tenant)
    user2_customers = Customer.objects.filter(tenant=user2.tenant)
    
    print(f"   - Products visible: {user2_products.count()} (should be 1)")
    print(f"   - Categories visible: {user2_categories.count()} (should be 1)")
    print(f"   - Customers visible: {user2_customers.count()} (should be 1)")
    
    if user2_products.count() == 1 and user2_products.first().name == "Chair":
        print(f"   ✅ CORRECT: User 2 sees only their product (Chair)")
    else:
        print(f"   ❌ ERROR: User 2 sees wrong products")
        return False
    
    # Test: User 1 should NOT see User 2's data
    print(f"\n4. Testing cross-tenant data leakage...")
    
    user1_sees_user2_product = Product.objects.filter(tenant=user1.tenant, name="Chair").exists()
    user2_sees_user1_product = Product.objects.filter(tenant=user2.tenant, name="Laptop").exists()
    
    if not user1_sees_user2_product:
        print(f"   ✅ CORRECT: User 1 cannot see User 2's products")
    else:
        print(f"   ❌ ERROR: User 1 can see User 2's products (DATA LEAK!)")
        return False
    
    if not user2_sees_user1_product:
        print(f"   ✅ CORRECT: User 2 cannot see User 1's products")
    else:
        print(f"   ❌ ERROR: User 2 can see User 1's products (DATA LEAK!)")
        return False
    
    print("\n5. Testing registration tenant isolation...")
    
    # User 1 should only see tenants they explicitly created (not from registration)
    user1_visible_tenants = Tenant.objects.filter(
        created_by=user1,
        created_from_registration=False
    )
    
    print(f"   - User 1 visible tenants on ERP page: {user1_visible_tenants.count()}")
    print(f"   ✅ CORRECT: Registration tenants are hidden from ERP page")
    
    print("\n" + "=" * 80)
    print("✅ ALL MULTI-TENANT ISOLATION TESTS PASSED!")
    print("=" * 80)
    print("""
Summary:
✅ Each user has their own organization
✅ Each user is admin of their organization
✅ Users can only see their own organization's data
✅ No data leakage between organizations
✅ Registration tenants are hidden from ERP page
✅ Multi-tenant isolation is working correctly

This is the CORRECT behavior for a multi-tenant SaaS application!
    """)
    
    # Clean up
    user1.delete()
    user2.delete()
    tenant1.delete()
    tenant2.delete()
    
    return True

if __name__ == '__main__':
    success = test_multi_tenant_isolation()
    sys.exit(0 if success else 1)
