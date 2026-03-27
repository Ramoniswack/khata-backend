#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from sales.models import Customer, Invoice
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()

# Get user and customer
user = User.objects.filter(tenant__isnull=False, email="admin@khata.com").first()
customer = Customer.objects.filter(tenant=user.tenant).first()

print(f"Creating invoice for {customer.name} in tenant {user.tenant.name}")

# Create invoice directly
invoice = Invoice.objects.create(
    tenant=user.tenant,
    invoice_number="INV-TEST-001",
    customer=customer,
    date=date.today(),
    due_date=date.today() + timedelta(days=30),
    amount=Decimal("5000.00"),
    paid_amount=Decimal("5000.00"),
    payment_type="cash",
    status="Paid",
    notes="Test invoice with payment at creation",
    created_by=user
)

print(f"✅ Invoice created: {invoice.invoice_number}")
print(f"   Status: {invoice.status}")
print(f"   Amount: Rs. {invoice.amount}")
print(f"   Paid: Rs. {invoice.paid_amount}")
print(f"   Balance: Rs. {invoice.balance}")

# Cleanup
invoice.delete()
print(f"✅ Invoice deleted")
