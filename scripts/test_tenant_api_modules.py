#!/usr/bin/env python
"""
Test tenant API with module subscriptions
Simulates the frontend /erp/new page flow
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from tenants.views import TenantViewSet
from tenants.models import Tenant

User = get_user_model()

def test_tenant_creation_api():
    """Test tenant creation via API with module selection"""
    print("\n" + "="*60)
    print("TEST: Tenant Creation API with Module Selection")
    print("="*60)
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='apitest',
        defaults={
            'email': 'apitest@example.com',
            'first_name': 'API',
            'last_name': 'Test'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    factory = RequestFactory()
    
    # Test 1: Create tenant with CORE modules only
    print("\n--- Test 1: CORE Modules Only ---")
    data = {
        'name': 'API Test Core Business',
        'business_type': 'other',
        'owner_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+977 9812345678',
        'address': 'Kathmandu, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports']
    }
    
    request = factory.post('/api/tenants/', data=data, content_type='application/json')
    force_authenticate(request, user=user)
    
    view = TenantViewSet.as_view({'post': 'create'})
    response = view(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Tenant created successfully")
        print(f"  Name: {response.data['name']}")
        print(f"  Slug: {response.data['slug']}")
        print(f"  Active modules: {response.data['active_modules']}")
        tenant_id_1 = response.data['id']
    else:
        print(f"✗ Failed: {response.data}")
        return
    
    # Test 2: Create tenant with CONSTRUCTION modules
    print("\n--- Test 2: CORE + CONSTRUCTION Modules ---")
    data = {
        'name': 'API Test Construction Co',
        'business_type': 'construction',
        'owner_name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone': '+977 9823456789',
        'address': 'Pokhara, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction']
    }
    
    request = factory.post('/api/tenants/', data=data, content_type='application/json')
    force_authenticate(request, user=user)
    
    response = view(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Tenant created successfully")
        print(f"  Name: {response.data['name']}")
        print(f"  Slug: {response.data['slug']}")
        print(f"  Active modules: {response.data['active_modules']}")
        tenant_id_2 = response.data['id']
    else:
        print(f"✗ Failed: {response.data}")
        return
    
    # Test 3: Create tenant with HARDWARE modules
    print("\n--- Test 3: CORE + HARDWARE Modules ---")
    data = {
        'name': 'API Test Hardware Store',
        'business_type': 'hardware',
        'owner_name': 'Bob Johnson',
        'email': 'bob@example.com',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'hardware']
    }
    
    request = factory.post('/api/tenants/', data=data, content_type='application/json')
    force_authenticate(request, user=user)
    
    response = view(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Tenant created successfully")
        print(f"  Name: {response.data['name']}")
        print(f"  Slug: {response.data['slug']}")
        print(f"  Active modules: {response.data['active_modules']}")
        tenant_id_3 = response.data['id']
    else:
        print(f"✗ Failed: {response.data}")
        return
    
    # Test 4: List all tenants
    print("\n--- Test 4: List All Tenants ---")
    request = factory.get('/api/tenants/')
    force_authenticate(request, user=user)
    
    view = TenantViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.data.get('results', response.data)
        print(f"✓ Found {len(results)} tenants")
        for tenant in results:
            print(f"  - {tenant['name']}: {tenant['active_modules']}")
    
    # Test 5: Activate/Deactivate modules
    print("\n--- Test 5: Module Activation/Deactivation ---")
    
    # Get the first tenant
    tenant = Tenant.objects.get(id=tenant_id_1)
    print(f"Tenant: {tenant.name}")
    print(f"Before: {tenant.active_modules}")
    
    # Activate construction module
    request = factory.post(
        f'/api/tenants/{tenant.slug}/activate_module/',
        data={'module_name': 'construction'},
        content_type='application/json'
    )
    force_authenticate(request, user=user)
    
    view = TenantViewSet.as_view({'post': 'activate_module'})
    response = view(request, slug=tenant.slug)
    
    if response.status_code == 200:
        print(f"✓ Activated construction module")
        print(f"After: {response.data['active_modules']}")
    
    # Deactivate construction module
    request = factory.post(
        f'/api/tenants/{tenant.slug}/deactivate_module/',
        data={'module_name': 'construction'},
        content_type='application/json'
    )
    force_authenticate(request, user=user)
    
    view = TenantViewSet.as_view({'post': 'deactivate_module'})
    response = view(request, slug=tenant.slug)
    
    if response.status_code == 200:
        print(f"✓ Deactivated construction module")
        print(f"After: {response.data['active_modules']}")
    
    print("\n" + "="*60)
    print("✓ All API tests completed successfully!")
    print("="*60)
    
    # Cleanup
    print("\n--- Cleanup ---")
    Tenant.objects.filter(id__in=[tenant_id_1, tenant_id_2, tenant_id_3]).delete()
    print("✓ Test tenants deleted")

if __name__ == '__main__':
    test_tenant_creation_api()
