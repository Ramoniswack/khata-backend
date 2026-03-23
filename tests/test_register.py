#!/usr/bin/env python
"""
Test registration endpoint to debug 500 error
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.serializers import RegisterSerializer
from users.models import User
from tenants.models import Tenant

# Test data
test_data = {
    'tenant_name': 'Test Company',
    'username': 'testuser123',
    'email': 'test@example.com',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'User',
    'phone': '+977 9800000000',
}

print("Testing RegisterSerializer...")
print(f"Test data: {test_data}")
print()

try:
    serializer = RegisterSerializer(data=test_data)
    
    if serializer.is_valid():
        print("✓ Serializer validation passed")
        print(f"Validated data: {serializer.validated_data}")
        print()
        
        # Try to create user
        print("Creating user...")
        user = serializer.save()
        print(f"✓ User created successfully: {user}")
        print(f"  - ID: {user.id}")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Role: {user.role}")
        print(f"  - Tenant: {user.tenant}")
        
        # Clean up
        if user.tenant:
            print(f"\nCleaning up tenant: {user.tenant.name}")
            user.tenant.delete()  # This will cascade delete the user
        else:
            print(f"\nCleaning up user: {user.username}")
            user.delete()
        
        print("\n✓ Test completed successfully!")
        
    else:
        print("✗ Serializer validation failed")
        print(f"Errors: {serializer.errors}")
        
except Exception as e:
    print(f"\n✗ Error occurred: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
