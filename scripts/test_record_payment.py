#!/usr/bin/env python
"""
Test record payment functionality
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
from sales.models import Customer, Invoice

User = get_user_model()

print("\n" + "="*80)
print("TESTING RECORD PAYMENT FUNCTIONALITY")
print("="*80)

# Get a user with invoices
users_with_invoices = []
for user in User.objects.all():
    if user.tenant:
        invoices = Invoice.objects.filter(tenant=user.tenant)
        if invoices.count() > 0:
            users_with_invoices.append((user, invoices))

if not users_with_invoices:
    print("\n❌ No users with invoices found!")
    print("\nPlease create an invoice first")
    sys.exit(1)

# Use the first user with invoices
user, invoices = users_with_invoices[0]
invoice = invoices.first()

print(f"\n[1] Using User: {user.username}")
print(f"    Tenant: {user.tenant.name}")
print(f"    Invoice: {invoice.invoice_number}")
print(f"    Amount: Rs. {invoice.amount}")
print(f"    Paid: Rs. {invoice.paid_amount}")
print(f"    Balance: Rs. {invoice.balance}")
print(f"    Status: {invoice.status}")

# Setup API client
client = APIClient()
client.force_authenticate(user=user)
client.defaults['HTTP_HOST'] = 'localhost:8000'

# Test recording a payment
payment_amount = float(invoice.balance) / 2  # Pay half

print(f"\n[2] Recording payment of Rs. {payment_amount}")

try:
    response = client.post(
        f'/api/sales/invoices/{invoice.id}/record_payment/',
        {'amount': payment_amount},
        format='json'
    )
    
    print(f"\n[3] Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        print("\nResponse Data:")
        print(json.dumps(response.data, indent=2, default=str))
        
        # Verify the payment was recorded
        invoice.refresh_from_db()
        print(f"\n[4] Updated Invoice:")
        print(f"    Paid: Rs. {invoice.paid_amount}")
        print(f"    Balance: Rs. {invoice.balance}")
        print(f"    Status: {invoice.status}")
    else:
        print("\n❌ FAILED!")
        print("\nError Response:")
        try:
            print(json.dumps(response.data, indent=2, default=str))
        except:
            print(response.content.decode())
        
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
