#!/usr/bin/env python
"""
Comprehensive test for tenant deletion with all edge cases
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework import status
from tenants.views import TenantViewSet

User = get_user_model()

def test_tenant_deletion():
    print("=" * 70)
    print("COMPREHENSIVE TENANT DELETION TEST")
    print("=" * 70)
    
    # Clean up any existing test data
    print("   Cleaning up existing test data...")
    
    # Delete tenants with related data cleanup
    from hr.models import Employee, Department
    
    test_tenants = list(Tenant.objects.filter(name__in=['Test Org for Deletion', 'Test Org for Deletion 2', 'Other Org']))
    for tenant in test_tenants:
        # Delete related HR data first
        Employee.objects.filter(tenant=tenant).delete()
        Department.objects.filter(tenant=tenant).delete()
        # Unassign users
        User.objects.filter(tenant=tenant).update(tenant=None)
        tenant.delete()
    
    User.objects.filter(email__in=[
        'creator@test.com',
        'admin@test.com',
        'manager@test.com',
        'viewer@test.com',
        'outsider@test.com'
    ]).delete()
    
    # Create test users
    print("\n1. Creating test users...")
    creator = User.objects.create_user(
        username='creator',
        email='creator@test.com',
        password='test123',
        role='admin'
    )
    
    admin_user = User.objects.create_user(
        username='admin_user',
        email='admin@test.com',
        password='test123',
        role='admin'
    )
    
    manager_user = User.objects.create_user(
        username='manager_user',
        email='manager@test.com',
        password='test123',
        role='manager'
    )
    
    viewer_user = User.objects.create_user(
        username='viewer_user',
        email='viewer@test.com',
        password='test123',
        role='viewer'
    )
    
    outsider = User.objects.create_user(
        username='outsider',
        email='outsider@test.com',
        password='test123',
        role='admin'
    )
    
    print(f"✅ Created 5 test users")
    
    # Create test organization
    print("\n2. Creating test organization...")
    tenant = Tenant.objects.create(
        name='Test Org for Deletion',
        business_type='construction',
        created_by=creator,
        created_from_registration=False
    )
    
    # Assign users to tenant
    creator.tenant = tenant
    creator.save()
    
    admin_user.tenant = tenant
    admin_user.save()
    
    manager_user.tenant = tenant
    manager_user.save()
    
    viewer_user.tenant = tenant
    viewer_user.save()
    
    # Outsider has different tenant
    other_tenant = Tenant.objects.create(
        name='Other Org',
        business_type='hardware',
        created_by=outsider,
        created_from_registration=False
    )
    outsider.tenant = other_tenant
    outsider.save()
    
    print(f"✅ Created organization: {tenant.name} (slug: {tenant.slug})")
    print(f"   Members: creator (admin), admin_user (admin), manager (manager), viewer (viewer)")
    print(f"   Outsider in different org: {other_tenant.name}")
    
    # Test cases using ViewSet directly (avoids middleware issues)
    factory = APIRequestFactory()
    
    # TEST 1: Viewer cannot delete
    print("\n3. TEST 1: Viewer cannot delete organization")
    request = factory.delete(f'/api/tenants/{tenant.slug}/')
    force_authenticate(request, user=viewer_user)
    
    viewset = TenantViewSet.as_view({'delete': 'destroy'})
    response = viewset(request, slug=tenant.slug)
    
    if response.status_code == 403:
        print(f"✅ PASS: Viewer got 403 Forbidden")
        print(f"   Error: {response.data.get('detail', 'No detail')}")
    else:
        print(f"❌ FAIL: Expected 403, got {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Response: {response.data}")
    
    # TEST 2: Manager cannot delete
    print("\n4. TEST 2: Manager cannot delete organization")
    request = factory.delete(f'/api/tenants/{tenant.slug}/')
    force_authenticate(request, user=manager_user)
    
    viewset = TenantViewSet.as_view({'delete': 'destroy'})
    response = viewset(request, slug=tenant.slug)
    
    if response.status_code == 403:
        print(f"✅ PASS: Manager got 403 Forbidden")
        print(f"   Error: {response.data.get('detail', 'No detail')}")
    else:
        print(f"❌ FAIL: Expected 403, got {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Response: {response.data}")
    
    # TEST 3: Outsider admin cannot delete
    print("\n5. TEST 3: Outsider admin cannot delete organization")
    request = factory.delete(f'/api/tenants/{tenant.slug}/')
    force_authenticate(request, user=outsider)
    
    viewset = TenantViewSet.as_view({'delete': 'destroy'})
    response = viewset(request, slug=tenant.slug)
    
    if response.status_code == 404:
        print(f"✅ PASS: Outsider got 404 Not Found (not in queryset)")
    elif response.status_code == 403:
        print(f"✅ PASS: Outsider got 403 Forbidden")
        print(f"   Error: {response.data.get('detail', 'No detail')}")
    else:
        print(f"❌ FAIL: Expected 404 or 403, got {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Response: {response.data}")
    
    # TEST 4: Admin member CAN delete
    print("\n6. TEST 4: Admin member CAN delete organization")
    request = factory.delete(f'/api/tenants/{tenant.slug}/')
    force_authenticate(request, user=admin_user)
    
    viewset = TenantViewSet.as_view({'delete': 'destroy'})
    response = viewset(request, slug=tenant.slug)
    
    if response.status_code == 204:
        print(f"✅ PASS: Admin member successfully deleted organization")
        
        # Verify users were unassigned
        creator.refresh_from_db()
        admin_user.refresh_from_db()
        manager_user.refresh_from_db()
        viewer_user.refresh_from_db()
        
        if not creator.tenant and not admin_user.tenant and not manager_user.tenant and not viewer_user.tenant:
            print(f"✅ All users unassigned from tenant")
        else:
            print(f"❌ Some users still have tenant assigned")
        
        # Verify tenant was deleted
        if not Tenant.objects.filter(slug=tenant.slug).exists():
            print(f"✅ Tenant deleted from database")
        else:
            print(f"❌ Tenant still exists in database")
    else:
        print(f"❌ FAIL: Expected 204, got {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Response: {response.data}")
        
        # If admin couldn't delete, try with creator
        print("\n7. TEST 5: Creator CAN delete organization (fallback)")
        
        # Recreate tenant if it was deleted
        if not Tenant.objects.filter(slug=tenant.slug).exists():
            tenant = Tenant.objects.create(
                name='Test Org for Deletion 2',
                business_type='construction',
                created_by=creator,
                created_from_registration=False
            )
            creator.tenant = tenant
            creator.save()
        
        request = factory.delete(f'/api/tenants/{tenant.slug}/')
        force_authenticate(request, user=creator)
        
        viewset = TenantViewSet.as_view({'delete': 'destroy'})
        response = viewset(request, slug=tenant.slug)
        
        if response.status_code == 204:
            print(f"✅ PASS: Creator successfully deleted organization")
        else:
            print(f"❌ FAIL: Expected 204, got {response.status_code}")
            if hasattr(response, 'data'):
                print(f"   Response: {response.data}")
    
    # Cleanup
    print("\n8. Cleaning up test data...")
    from hr.models import Employee, Department
    
    # Delete tenants with related data cleanup
    test_tenants = list(Tenant.objects.filter(name__in=['Test Org for Deletion', 'Test Org for Deletion 2', 'Other Org']))
    for tenant in test_tenants:
        Employee.objects.filter(tenant=tenant).delete()
        Department.objects.filter(tenant=tenant).delete()
        User.objects.filter(tenant=tenant).update(tenant=None)
        tenant.delete()
    
    User.objects.filter(email__in=[
        'creator@test.com',
        'admin@test.com',
        'manager@test.com',
        'viewer@test.com',
        'outsider@test.com'
    ]).delete()
    
    print("✅ Cleanup complete")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_tenant_deletion()
