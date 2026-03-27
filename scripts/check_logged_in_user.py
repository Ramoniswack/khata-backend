#!/usr/bin/env python
"""
Check which user is currently logged in via the frontend
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

User = get_user_model()

print("\n" + "="*80)
print("CHECKING USER DATA FOR INVOICE CREATION")
print("="*80)

# Check all users and their data
print("\n[1] All Users with Customers:")
users_with_customers = []
users_without_customers = []

for user in User.objects.all():
    if not user.tenant:
        continue
    
    customers = Customer.objects.filter(tenant=user.tenant)
    if customers.count() > 0:
        users_with_customers.append((user, customers))
    else:
        users_without_customers.append(user)
for user in User.objects.all():
    if not user.tenant:
        continue
    
    customers = Customer.objects.filter(tenant=user.tenant)
    if customers.count() > 0:
        users_with_customers.append((user, customers))
    else:
        users_without_customers.append(user)

print(f"\nUsers WITH customers: {len(users_with_customers)}")
for user, customers in users_with_customers[:5]:
    print(f"\n  • {user.username} (Tenant: {user.tenant.name})")
    print(f"    Customers: {customers.count()}")
    for customer in customers[:2]:
        print(f"      - {customer.name} (ID: {customer.id})")

print(f"\n\nUsers WITHOUT customers: {len(users_without_customers)}")
for user in users_without_customers[:5]:
    print(f"  • {user.username} (Tenant: {user.tenant.name if user.tenant else 'NO TENANT'})")

print("\n" + "="*80)
print("TO FIX YOUR ISSUE:")
print("="*80)
print("\n1. Find out which user you're logged in as")
print("2. If that user has no customers, create one:")
print("   - Go to: http://localhost:3000/dashboard/sales/customers/new")
print("   - Or run: python scripts/create_test_customer.py <username>")
print("\n3. Then try creating an invoice again")
print("\n" + "="*80)
