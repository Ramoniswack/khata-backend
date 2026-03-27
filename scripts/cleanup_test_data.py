#!/usr/bin/env python
"""
Cleanup test data from previous test runs
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

print("Cleaning up test data...")

# Delete test users
print("- Deleting test users...")
User.objects.filter(email__in=['alice@test.com', 'bob@test.com']).delete()

# Delete test sales orders
print("- Deleting test sales orders...")
SalesOrder.objects.filter(order_number__in=['SO-ALICE-001', 'SO-BOB-001']).delete()

# Delete test customers
print("- Deleting test customers...")
Customer.objects.filter(email__in=['customer@alice.com', 'customer@bob.com']).delete()

# Delete test tenants
print("- Deleting test tenants...")
Tenant.objects.filter(name__in=['Alice Company', 'Bob Company']).delete()

print("✓ Cleanup complete!")
