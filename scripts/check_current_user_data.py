#!/usr/bin/env python
"""
Check current user's tenant and available customers
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
from tenants.models import Tenant

User = get_user_model()

print("\n" + "="*80)
print("CHECKING USER DATA FOR INVOICE CREATION")
print("="*80)

# List all users
print("\n[1] All Users:")
for user in User.objects.all():
    print(f"  - {user.username} (ID: {user.id})")
    if user.tenant:
        print(f"    Tenant: {user.tenant.name} (ID: {user.tenant.id})")
        customers = Customer.objects.filter(tenant=user.tenant)
        print(f"    Customers: {customers.count()}")
        for customer in customers[:5]:
            print(f"      • {customer.name} (ID: {customer.id})")
    else:
        print(f"    ⚠️  NO TENANT ASSIGNED!")
    print()

# List all tenants
print("\n[2] All Tenants:")
for tenant in Tenant.objects.all():
    print(f"  - {tenant.name} (Slug: {tenant.slug})")
    users = User.objects.filter(tenant=tenant)
    customers = Customer.objects.filter(tenant=tenant)
    print(f"    Users: {users.count()}, Customers: {customers.count()}")

# List all customers
print("\n[3] All Customers:")
for customer in Customer.objects.all():
    print(f"  - {customer.name} (ID: {customer.id})")
    print(f"    Tenant: {customer.tenant.name if customer.tenant else 'NO TENANT'}")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("\nIf you're logged in as a user without customers:")
print("1. Create a customer for your tenant via the UI")
print("2. Or run: python manage.py shell")
print("   Then create a customer for your tenant")
print("\n" + "="*80)
