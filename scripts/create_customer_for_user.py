#!/usr/bin/env python
"""
Create a test customer for a specific user
Usage: python scripts/create_customer_for_user.py <username>
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from sales.models import Customer

User = get_user_model()

if len(sys.argv) < 2:
    print("\n❌ Error: Please provide a username")
    print("Usage: python scripts/create_customer_for_user.py <username>")
    print("\nAvailable users:")
    for user in User.objects.all()[:10]:
        print(f"  - {user.username}")
    sys.exit(1)

username = sys.argv[1]

print("\n" + "="*80)
print(f"CREATING CUSTOMER FOR USER: {username}")
print("="*80)

try:
    user = User.objects.get(username=username)
    print(f"\n✓ Found user: {user.username}")
    
    if not user.tenant:
        print(f"\n❌ Error: User has no tenant assigned!")
        sys.exit(1)
    
    print(f"✓ Tenant: {user.tenant.name}")
    
    # Check existing customers
    existing = Customer.objects.filter(tenant=user.tenant)
    print(f"\nExisting customers: {existing.count()}")
    
    # Create a test customer
    customer = Customer.objects.create(
        tenant=user.tenant,
        name="Test Customer",
        phone="9876543210",
        email="customer@test.com",
        type="Individual",
        credit_limit=100000,
        payment_terms="Net 30",
        status="active"
    )
    
    print(f"\n✅ Created customer: {customer.name} (ID: {customer.id})")
    print(f"   Phone: {customer.phone}")
    print(f"   Email: {customer.email}")
    print(f"   Credit Limit: Rs. {customer.credit_limit:,.0f}")
    
    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print("\nYou can now create invoices at:")
    print("http://localhost:3000/dashboard/sales/invoices/new")
    print("\n" + "="*80)
    
except User.DoesNotExist:
    print(f"\n❌ Error: User '{username}' not found!")
    print("\nAvailable users:")
    for user in User.objects.all()[:10]:
        print(f"  - {user.username}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
