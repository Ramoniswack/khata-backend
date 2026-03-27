#!/usr/bin/env python
"""
Test invoice creation with a real user (simulating frontend request)
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from sales.models import Customer

User = get_user_model()

print("\n" + "="*80)
print("TESTING INVOICE CREATION WITH REAL USER")
print("="*80)

# Get a user with customers
users_with_customers = []
for user in User.objects.all():
    if user.tenant:
        customers = Customer.objects.filter(tenant=user.tenant)
        if customers.count() > 0:
            users_with_customers.append((user, customers))

if not users_with_customers:
    print("\n❌ No users with customers found!")
    print("\nPlease create a customer first:")
    print("1. Go to: http://localhost:3000/dashboard/sales/customers/new")
    print("2. Or run: python scripts/create_customer_for_user.py <username>")
    sys.exit(1)

# Use the first user with customers
user, customers = users_with_customers[0]
customer = customers.first()

print(f"\n[1] Using User: {user.username}")
print(f"    Tenant: {user.tenant.name}")
print(f"    Customer: {customer.name} (ID: {customer.id})")

# Setup API client
client = APIClient()
client.force_authenticate(user=user)
client.defaults['HTTP_HOST'] = 'localhost:8000'

# Test data (exact format from frontend)
invoice_data = {
    "customer": str(customer.id),
    "date": "2026-03-26",
    "due_date": "2026-04-25",
    "amount": 5000.0,
    "payment_type": "cash",
    "status": "Draft",
    "notes": "Test invoice"
}

print("\n[2] Request Data:")
print(json.dumps(invoice_data, indent=2))

# Make the request
print("\n[3] Creating invoice...")
try:
    response = client.post('/api/sales/invoices/', invoice_data, format='json')
    
    print(f"\n[4] Response Status: {response.status_code}")
    
    if response.status_code == 201:
        print("\n✅ SUCCESS!")
        print("\nResponse Data:")
        print(json.dumps(response.data, indent=2, default=str))
    else:
        print("\n❌ FAILED!")
        print("\nError Response:")
        try:
            print(json.dumps(response.data, indent=2, default=str))
        except:
            print(response.content.decode())
        
        # Show more debug info
        print("\n" + "-"*80)
        print("DEBUG INFO:")
        print("-"*80)
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Tenant: {user.tenant.name} (ID: {user.tenant.id})")
        print(f"Customer: {customer.name} (ID: {customer.id})")
        print(f"Customer Tenant: {customer.tenant.name} (ID: {customer.tenant.id})")
        print(f"Tenants Match: {user.tenant == customer.tenant}")
        
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
