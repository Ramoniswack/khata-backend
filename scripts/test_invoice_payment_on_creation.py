#!/usr/bin/env python
"""
Test invoice creation with immediate payment recording
Simulates the frontend flow: create invoice with status "Sent" then record payment
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from sales.models import Customer, Invoice
from decimal import Decimal
import requests

User = get_user_model()

def test_invoice_payment_flow():
    """Test the complete flow: create invoice + record payment"""
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False, email="admin@khata.com").first()
    if not user:
        # Try any user
        user = User.objects.filter(tenant__isnull=False).first()
    
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"✅ Using user: {user.email} (Tenant: {user.tenant.name})")
    
    # Get or create a customer
    customer = Customer.objects.filter(tenant=user.tenant).first()
    if not customer:
        print("⚠️  No customer found, creating one...")
        customer = Customer.objects.create(
            tenant=user.tenant,
            name="Test Customer",
            phone="9876543210",
            email="test@customer.com",
            type="Individual",
            payment_terms="Net 30",
            status="active"
        )
        print(f"✅ Created customer: {customer.name}")
    else:
        print(f"✅ Using customer: {customer.name}")
    
    # Login to get token
    login_url = "http://localhost:8000/api/auth/login/"
    
    # Try common passwords
    passwords = ["Admin@123", "admin123", "password", "Admin123"]
    token = None
    
    for pwd in passwords:
        login_data = {
            "email": user.email,
            "password": pwd
        }
        
        print(f"\n📡 Logging in with password: {pwd}...")
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            token = response.json()['access']
            print(f"✅ Login successful with password: {pwd}")
            break
    
    if not token:
        print(f"❌ Login failed with all passwords")
        print(f"💡 Please create a test user or update the password in the script")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create invoice with status "Sent"
    invoice_data = {
        "customer": str(customer.id),
        "date": "2024-03-27",
        "due_date": "2024-04-27",
        "amount": 5000.00,
        "payment_type": "cash",
        "status": "Sent",
        "notes": "Test invoice for payment recording"
    }
    
    print(f"\n📡 Creating invoice with status 'Sent'...")
    create_url = "http://localhost:8000/api/sales/invoices/"
    response = requests.post(create_url, json=invoice_data, headers=headers)
    
    if response.status_code != 201:
        print(f"❌ Invoice creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    invoice_response = response.json()
    invoice_id = invoice_response['id']
    invoice_number = invoice_response['invoice_number']
    print(f"✅ Invoice created: {invoice_number} (ID: {invoice_id})")
    print(f"   Status: {invoice_response['status']}")
    print(f"   Amount: Rs. {invoice_response['amount']}")
    
    # Now try to record payment
    payment_amount = 5000.00
    payment_url = f"http://localhost:8000/api/sales/invoices/{invoice_id}/record_payment/"
    payment_data = {
        "amount": payment_amount
    }
    
    print(f"\n📡 Recording payment of Rs. {payment_amount}...")
    response = requests.post(payment_url, json=payment_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Payment recording failed: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"\n🔍 Debugging info:")
        print(f"   Invoice ID: {invoice_id}")
        print(f"   Payment amount: {payment_amount}")
        print(f"   Invoice amount: {invoice_response['amount']}")
        return
    
    payment_response = response.json()
    print(f"✅ Payment recorded successfully!")
    print(f"   Invoice status: {payment_response['status']}")
    print(f"   Paid amount: Rs. {payment_response['paid_amount']}")
    print(f"   Balance: Rs. {payment_response['balance']}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test invoice...")
    Invoice.objects.filter(id=invoice_id).delete()
    print(f"✅ Test invoice deleted")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Invoice Creation + Payment Recording Flow")
    print("=" * 60)
    test_invoice_payment_flow()
    print("\n" + "=" * 60)
