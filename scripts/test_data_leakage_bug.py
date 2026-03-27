#!/usr/bin/env python
"""
Test script to reproduce the data leakage bug
where two different users can see the same data
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
from sales.models import SalesOrder, Customer
from purchase.models import PurchaseOrder, Supplier
from django.test import RequestFactory
from rest_framework.test import force_authenticate

def test_data_leakage():
    """Test if two users can see each other's data"""
    
    print("=" * 80)
    print("TESTING DATA LEAKAGE BUG")
    print("=" * 80)
    
    # Clean up (delete in correct order to avoid foreign key constraints)
    print("\n0. Cleaning up any existing test data...")
    SalesOrder.objects.filter(order_number__in=['SO-ALICE-001', 'SO-BOB-001']).delete()
    Customer.objects.filter(email__in=['customer@alice.com', 'customer@bob.com']).delete()
    User.objects.filter(email__in=['alice@test.com', 'bob@test.com']).delete()
    Tenant.objects.filter(name__in=['Alice Company', 'Bob Company']).delete()
    print("   ✓ Cleanup complete")
    
    print("\n1. Creating User Alice with her company...")
    tenant_alice = Tenant.objects.create(
        name="Alice Company",
        business_type="retail",
        created_from_registration=True
    )
    user_alice = User.objects.create_user(
        username='alice',
        email='alice@test.com',
        password='test123',
        first_name='Alice',
        last_name='Smith',
        tenant=tenant_alice,
        role='admin'
    )
    tenant_alice.created_by = user_alice
    tenant_alice.save()
    
    print(f"   ✓ Alice: {user_alice.email}")
    print(f"   ✓ Tenant: {tenant_alice.name} (ID: {tenant_alice.id})")
    
    print("\n2. Creating User Bob with his company...")
    tenant_bob = Tenant.objects.create(
        name="Bob Company",
        business_type="wholesale",
        created_from_registration=True
    )
    user_bob = User.objects.create_user(
        username='bob',
        email='bob@test.com',
        password='test123',
        first_name='Bob',
        last_name='Jones',
        tenant=tenant_bob,
        role='admin'
    )
    tenant_bob.created_by = user_bob
    tenant_bob.save()
    
    print(f"   ✓ Bob: {user_bob.email}")
    print(f"   ✓ Tenant: {tenant_bob.name} (ID: {tenant_bob.id})")
    
    print("\n3. Alice creates a customer and sales order...")
    from datetime import date
    customer_alice = Customer.objects.create(
        name="Alice's Customer",
        email="customer@alice.com",
        tenant=tenant_alice
    )
    order_alice = SalesOrder.objects.create(
        customer=customer_alice,
        order_number="SO-ALICE-001",
        date=date.today(),
        tenant=tenant_alice,
        total=10000
    )
    print(f"   ✓ Created customer: {customer_alice.name}")
    print(f"   ✓ Created order: {order_alice.order_number}")
    
    print("\n4. Bob creates a customer and sales order...")
    customer_bob = Customer.objects.create(
        name="Bob's Customer",
        email="customer@bob.com",
        tenant=tenant_bob
    )
    order_bob = SalesOrder.objects.create(
        customer=customer_bob,
        order_number="SO-BOB-001",
        date=date.today(),
        tenant=tenant_bob,
        total=20000
    )
    print(f"   ✓ Created customer: {customer_bob.name}")
    print(f"   ✓ Created order: {order_bob.order_number}")
    
    print("\n5. Testing API access...")
    
    # Test Sales Order ViewSet
    from sales.views import SalesOrderViewSet
    from rest_framework.test import APIRequestFactory
    
    factory = APIRequestFactory()
    
    # Alice's request
    print("\n   Testing Alice's access to sales orders:")
    request_alice = factory.get('/api/sales/orders/')
    request_alice.user = user_alice
    force_authenticate(request_alice, user=user_alice)
    
    view = SalesOrderViewSet.as_view({'get': 'list'})
    response_alice = view(request_alice)
    
    print(f"   - Alice sees {len(response_alice.data.get('results', []))} orders")
    if response_alice.data.get('results'):
        for order in response_alice.data['results']:
            print(f"     • {order['order_number']} (Tenant ID: {order.get('tenant', 'N/A')})")
    
    # Bob's request
    print("\n   Testing Bob's access to sales orders:")
    request_bob = factory.get('/api/sales/orders/')
    request_bob.user = user_bob
    force_authenticate(request_bob, user=user_bob)
    
    response_bob = view(request_bob)
    
    print(f"   - Bob sees {len(response_bob.data.get('results', []))} orders")
    if response_bob.data.get('results'):
        for order in response_bob.data['results']:
            print(f"     • {order['order_number']} (Tenant ID: {order.get('tenant', 'N/A')})")
    
    print("\n6. Checking for data leakage...")
    
    # Check if Alice can see Bob's data
    alice_orders = response_alice.data.get('results', [])
    alice_sees_bob_order = any(o['order_number'] == 'SO-BOB-001' for o in alice_orders)
    
    # Check if Bob can see Alice's data
    bob_orders = response_bob.data.get('results', [])
    bob_sees_alice_order = any(o['order_number'] == 'SO-ALICE-001' for o in bob_orders)
    
    has_leakage = False
    
    if alice_sees_bob_order:
        print(f"   ❌ DATA LEAKAGE: Alice can see Bob's order!")
        has_leakage = True
    else:
        print(f"   ✅ CORRECT: Alice cannot see Bob's order")
    
    if bob_sees_alice_order:
        print(f"   ❌ DATA LEAKAGE: Bob can see Alice's order!")
        has_leakage = True
    else:
        print(f"   ✅ CORRECT: Bob cannot see Alice's order")
    
    # Check counts
    if len(alice_orders) != 1:
        print(f"   ❌ ERROR: Alice should see 1 order, but sees {len(alice_orders)}")
        has_leakage = True
    else:
        print(f"   ✅ CORRECT: Alice sees exactly 1 order (her own)")
    
    if len(bob_orders) != 1:
        print(f"   ❌ ERROR: Bob should see 1 order, but sees {len(bob_orders)}")
        has_leakage = True
    else:
        print(f"   ✅ CORRECT: Bob sees exactly 1 order (his own)")
    
    print("\n" + "=" * 80)
    if has_leakage:
        print("❌ DATA LEAKAGE DETECTED!")
        print("=" * 80)
        print("""
PROBLEM: Users can see each other's data!

This is a CRITICAL security issue. Possible causes:
1. ViewSet get_queryset() not filtering by tenant
2. Serializer not checking tenant
3. Middleware not setting tenant context
4. Missing tenant field in model
        """)
    else:
        print("✅ NO DATA LEAKAGE - ISOLATION WORKING CORRECTLY!")
        print("=" * 80)
    
    # Clean up (delete in correct order to avoid foreign key constraints)
    print("\n7. Cleaning up test data...")
    order_alice.delete()
    order_bob.delete()
    customer_alice.delete()
    customer_bob.delete()
    user_alice.delete()
    user_bob.delete()
    tenant_alice.delete()
    tenant_bob.delete()
    print("   ✓ Cleanup complete")
    
    return not has_leakage

if __name__ == '__main__':
    success = test_data_leakage()
    sys.exit(0 if success else 1)
