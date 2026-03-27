#!/usr/bin/env python
"""
Test invoice creation with paid_amount set at creation time
This simulates the new frontend flow where invoice is created as "Paid" directly
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

def test_invoice_paid_creation():
    """Test creating an invoice with paid_amount set at creation"""
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False, email="admin@khata.com").first()
    if not user:
        user = User.objects.filter(tenant__isnull=False).first()
    
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"✅ Using user: {user.email} (Tenant: {user.tenant.name})")
    
    # Get or create a customer
    customer = Customer.objects.filter(tenant=user.tenant).first()
    if not customer:
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
    
    passwords = ["Admin@123", "admin123", "password", "Admin123"]
    token = None
    
    for pwd in passwords:
        login_data = {"email": user.email, "password": pwd}
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token = response.json()['access']
            print(f"✅ Login successful")
            break
    
    if not token:
        print(f"❌ Login failed")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create invoice with paid_amount set (simulating "Record Payment" button)
    invoice_amount = 5000.00
    invoice_data = {
        "customer": str(customer.id),
        "date": "2024-03-27",
        "due_date": "2024-04-27",
        "amount": invoice_amount,
        "paid_amount": invoice_amount,  # Full payment at creation
        "payment_type": "cash",
        "status": "Paid",  # Status is Paid
        "notes": "Test invoice with payment at creation"
    }
    
    print(f"\n📡 Creating invoice with paid_amount={invoice_amount} and status='Paid'...")
    create_url = "http://localhost:8000/api/sales/invoices/"
    response = requests.post(create_url, json=invoice_data, headers=headers)
    
    if response.status_code != 201:
        print(f"❌ Invoice creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    invoice_response = response.json()
    invoice_id = invoice_response['id']
    invoice_number = invoice_response['invoice_number']
    print(f"✅ Invoice created successfully!")
    print(f"   Invoice: {invoice_number} (ID: {invoice_id})")
    print(f"   Status: {invoice_response['status']}")
    print(f"   Amount: Rs. {invoice_response['amount']}")
    print(f"   Paid Amount: Rs. {invoice_response['paid_amount']}")
    print(f"   Balance: Rs. {invoice_response['balance']}")
    
    # Verify the invoice is fully paid
    if invoice_response['status'] == 'Paid' and float(invoice_response['balance']) == 0:
        print(f"\n✅ SUCCESS: Invoice is fully paid!")
    else:
        print(f"\n⚠️  WARNING: Invoice status or balance is incorrect")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test invoice...")
    Invoice.objects.filter(id=invoice_id).delete()
    print(f"✅ Test invoice deleted")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Invoice Creation with Paid Amount")
    print("=" * 60)
    test_invoice_paid_creation()
    print("\n" + "=" * 60)
