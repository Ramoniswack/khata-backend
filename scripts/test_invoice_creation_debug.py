#!/usr/bin/env python
"""
Debug script to test invoice creation with exact frontend data
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
from tenants.models import Tenant

User = get_user_model()

print("\n" + "="*80)
print("TESTING INVOICE CREATION - DEBUG MODE")
print("="*80)

# Get or create test user
try:
    user = User.objects.get(username='testuser')
    tenant = user.tenant
    print(f"\n✓ Using existing user: {user.username}")
    print(f"✓ Tenant: {tenant.name}")
except User.DoesNotExist:
    print("\n❌ Test user not found. Creating...")
    tenant = Tenant.objects.create(name="Test Company", slug="test-company")
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        tenant=tenant
    )
    print(f"✓ Created user: {user.username}")
    print(f"✓ Created tenant: {tenant.name}")

# Get or create test customer
customer, created = Customer.objects.get_or_create(
    tenant=tenant,
    name="Test Customer",
    defaults={
        'phone': '1234567890',
        'email': 'customer@test.com',
        'type': 'Individual',
        'credit_limit': 100000,
        'payment_terms': 'Net 30',
        'status': 'active'
    }
)
print(f"\n✓ Customer: {customer.name} (ID: {customer.id})")

# Setup API client with proper host
client = APIClient()
client.force_authenticate(user=user)
# Set proper host header
client.defaults['HTTP_HOST'] = 'localhost:8000'

# Test data matching frontend request
invoice_data = {
    "customer": str(customer.id),
    "date": "2026-03-26",
    "due_date": "2026-04-25",
    "amount": 5000.0,
    "payment_type": "cash",
    "status": "Draft",
    "notes": "Test invoice from frontend"
}

print("\n" + "-"*80)
print("REQUEST DATA:")
print(json.dumps(invoice_data, indent=2))
print("-"*80)

# Make the request
print("\n[1] Creating invoice via API...")
response = client.post('/api/sales/invoices/', invoice_data, format='json')

print(f"\n[2] Response Status: {response.status_code}")

if response.status_code == 201:
    print("\n✅ SUCCESS! Invoice created")
    print("\nResponse Data:")
    try:
        print(json.dumps(response.data, indent=2, default=str))
    except:
        print(response.content.decode())
else:
    print("\n❌ FAILED!")
    print("\nError Response:")
    try:
        print(json.dumps(response.data, indent=2, default=str))
    except:
        print(response.content.decode())
    
    # Additional debugging
    print("\n" + "-"*80)
    print("DEBUGGING INFO:")
    print("-"*80)
    
    # Check if there are existing invoices
    from sales.models import Invoice
    existing_invoices = Invoice.objects.filter(tenant=tenant)
    print(f"\nExisting invoices for tenant: {existing_invoices.count()}")
    for inv in existing_invoices[:5]:
        print(f"  - {inv.invoice_number} (ID: {inv.id})")
    
    # Check customer
    print(f"\nCustomer exists: {Customer.objects.filter(id=customer.id, tenant=tenant).exists()}")
    print(f"Customer tenant: {customer.tenant.name}")
    print(f"User tenant: {user.tenant.name}")
    print(f"Tenants match: {customer.tenant == user.tenant}")

print("\n" + "="*80)
