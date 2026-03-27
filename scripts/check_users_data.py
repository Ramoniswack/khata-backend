#!/usr/bin/env python
"""
Check users data to debug the actions menu issue
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

print("=" * 60)
print("USERS DATA CHECK")
print("=" * 60)

# Get all users
users = User.objects.all()
print(f"\nTotal users: {users.count()}")

for user in users:
    print(f"\nUser ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Tenant: {user.tenant.name if user.tenant else 'None'}")
    print(f"  Is Active: {user.is_active}")

print("\n" + "=" * 60)
