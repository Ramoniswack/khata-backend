#!/usr/bin/env python
"""
Test that new user registration creates permissions correctly
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from users.permission_models import RolePermission

User = get_user_model()


def test_new_user_permissions():
    print("=" * 60)
    print("Test New User Registration Permissions")
    print("=" * 60)
    
    # Create a test user via the registration flow
    from users.serializers import RegisterSerializer
    
    test_data = {
        'email': 'testpermissions@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Permissions',
        'phone': '1234567890',
    }
    
    print("\n1. Creating new user via RegisterSerializer...")
    print(f"   Email: {test_data['email']}")
    
    # Clean up if user already exists
    User.objects.filter(email=test_data['email']).delete()
    
    serializer = RegisterSerializer(data=test_data)
    if not serializer.is_valid():
        print(f"   ❌ Validation failed: {serializer.errors}")
        return
    
    user = serializer.save()
    print(f"   ✅ User created: {user.username}")
    print(f"   ✅ Tenant created: {user.tenant.name}")
    print(f"   ✅ User role: {user.role}")
    
    # Check if permissions were initialized
    print("\n2. Checking permissions for new tenant...")
    tenant = user.tenant
    permissions = RolePermission.objects.filter(tenant=tenant)
    perm_count = permissions.count()
    
    print(f"   Total permissions: {perm_count}")
    
    if perm_count == 0:
        print("   ❌ NO PERMISSIONS FOUND! This is the bug.")
        return
    
    print(f"   ✅ Permissions initialized!")
    
    # Check permissions by role
    print("\n3. Checking permissions by role...")
    for role in ['admin', 'manager', 'supervisor', 'accountant', 'viewer']:
        role_perms = permissions.filter(role=role, allowed=True)
        print(f"   {role.capitalize()}: {role_perms.count()} permissions")
    
    # Check admin permissions for key modules
    print("\n4. Checking admin permissions for key modules...")
    admin_perms = permissions.filter(role='admin', allowed=True)
    
    modules_to_check = ['sales', 'purchase', 'inventory', 'accounting', 'construction']
    for module in modules_to_check:
        module_perms = admin_perms.filter(module=module)
        actions = list(module_perms.values_list('action', flat=True))
        print(f"   {module.capitalize()}: {', '.join(actions)}")
    
    # Simulate sidebar check
    print("\n5. Simulating sidebar permission checks...")
    
    def check_can_view(role, module):
        """Simulate the canView() check from frontend"""
        perm = RolePermission.objects.filter(
            tenant=tenant,
            role=role,
            module=module,
            action='view',
            allowed=True
        ).exists()
        return perm
    
    modules = ['sales', 'purchase', 'inventory', 'accounting', 'construction', 'hr', 'pos']
    
    print(f"\n   Checking as Admin (user's role):")
    for module in modules:
        can_view = check_can_view('admin', module)
        status = "✅ SHOW" if can_view else "❌ HIDE"
        print(f"   {status} {module.capitalize()} module")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    
    # Cleanup
    print("\nCleaning up test data...")
    user.delete()
    tenant.delete()
    print("✅ Cleanup complete")


if __name__ == '__main__':
    test_new_user_permissions()
