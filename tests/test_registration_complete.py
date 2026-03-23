#!/usr/bin/env python
"""
Test complete registration flow with all error cases
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.serializers import RegisterSerializer
from users.models import User
from tenants.models import Tenant

print("=" * 60)
print("COMPLETE REGISTRATION FLOW TEST")
print("=" * 60)

# Test 1: Successful registration
print("\n1. TEST: Successful registration")
print("-" * 60)
data1 = {
    'tenant_name': 'Unique Test Company',
    'username': 'uniqueuser',
    'email': 'unique@example.com',
    'password': 'testpass123',
    'first_name': 'Unique',
    'last_name': 'User',
    'phone': '+977 9800000000',
}

try:
    serializer = RegisterSerializer(data=data1)
    if serializer.is_valid():
        user = serializer.save()
        print(f"✓ SUCCESS: User created")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Role: {user.role}")
        print(f"  - Tenant: {user.tenant.name} (slug: {user.tenant.slug})")
    else:
        print(f"✗ FAILED: {serializer.errors}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test 2: Duplicate organization name
print("\n2. TEST: Duplicate organization name")
print("-" * 60)
data2 = {
    'tenant_name': 'Unique Test Company',  # Same as above
    'username': 'anotheruser',
    'email': 'another@example.com',
    'password': 'testpass123',
    'first_name': 'Another',
    'last_name': 'User',
}

try:
    serializer = RegisterSerializer(data=data2)
    if serializer.is_valid():
        user = serializer.save()
        print(f"✗ UNEXPECTED: Should have failed but succeeded")
    else:
        print(f"✓ EXPECTED FAILURE: {serializer.errors}")
except Exception as e:
    print(f"✓ EXPECTED ERROR: {e}")

# Test 3: Duplicate username
print("\n3. TEST: Duplicate username")
print("-" * 60)
data3 = {
    'tenant_name': 'Another Company',
    'username': 'uniqueuser',  # Same as test 1
    'email': 'different@example.com',
    'password': 'testpass123',
    'first_name': 'Different',
    'last_name': 'User',
}

try:
    serializer = RegisterSerializer(data=data3)
    if serializer.is_valid():
        user = serializer.save()
        print(f"✗ UNEXPECTED: Should have failed but succeeded")
    else:
        print(f"✓ EXPECTED FAILURE: {serializer.errors}")
except Exception as e:
    print(f"✓ EXPECTED ERROR: {e}")

# Test 4: Duplicate email
print("\n4. TEST: Duplicate email")
print("-" * 60)
data4 = {
    'tenant_name': 'Yet Another Company',
    'username': 'yetanotheruser',
    'email': 'unique@example.com',  # Same as test 1
    'password': 'testpass123',
    'first_name': 'Yet',
    'last_name': 'Another',
}

try:
    serializer = RegisterSerializer(data=data4)
    if serializer.is_valid():
        user = serializer.save()
        print(f"✗ UNEXPECTED: Should have failed but succeeded")
    else:
        print(f"✓ EXPECTED FAILURE: {serializer.errors}")
except Exception as e:
    print(f"✓ EXPECTED ERROR: {e}")

# Clean up
print("\n5. CLEANUP")
print("-" * 60)
test_tenants = Tenant.objects.filter(name__icontains='Test Company')
count = test_tenants.count()
test_tenants.delete()
print(f"✓ Deleted {count} test tenant(s)")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
