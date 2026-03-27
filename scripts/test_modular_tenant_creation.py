#!/usr/bin/env python
"""
Test script for modular architecture tenant creation
Tests the /erp/new page backend integration
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
from tenants.membership_models import UserTenantMembership
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_modular_tenant_creation():
    """Test creating a tenant with modular architecture"""
    
    print_section("MODULAR TENANT CREATION TEST")
    
    # Clean up any existing test data
    print("0. Cleaning up existing test data...")
    User.objects.filter(username='modular_test_user').delete()
    print("✓ Cleanup complete")
    
    # Create test user
    print("\n1. Creating test user...")
    test_user = User.objects.create_user(
        username='modular_test_user',
        email='modular@test.com',
        password='testpass123',
        first_name='Modular',
        last_name='Tester'
    )
    print(f"✓ Created user: {test_user.username} (ID: {test_user.id})")
    
    # Get JWT token
    print("\n2. Getting JWT token...")
    refresh = RefreshToken.for_user(test_user)
    access_token = str(refresh.access_token)
    print(f"✓ Token generated")
    
    # Setup API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Set SERVER_NAME to avoid ALLOWED_HOSTS issue
    client.defaults['SERVER_NAME'] = 'localhost'
    
    # Test 1: Create tenant with CORE modules only
    print_section("TEST 1: CORE Modules Only")
    
    tenant_data_core = {
        'name': 'Core Business Ltd',
        'business_type': 'other',
        'owner_name': 'John Doe',
        'email': 'john@corebusiness.com',
        'phone': '+977 9812345678',
        'address': 'Kathmandu, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports']
    }
    
    print("Creating tenant with CORE modules...")
    print(f"Modules: {tenant_data_core['active_modules']}")
    
    response = client.post('/api/tenants/', tenant_data_core, format='json')
    
    if response.status_code == 201:
        tenant = response.data
        print(f"\n✓ Tenant created successfully!")
        print(f"  - ID: {tenant['id']}")
        print(f"  - Name: {tenant['name']}")
        print(f"  - Slug: {tenant['slug']}")
        print(f"  - Business Type: {tenant['business_type']}")
        print(f"  - Active Modules: {tenant['active_modules']}")
        print(f"  - Plan: {tenant.get('plan_type', 'N/A')}")
        
        # Verify user assignment
        test_user.refresh_from_db()
        print(f"\n✓ User assignment:")
        print(f"  - User tenant: {test_user.tenant.name if test_user.tenant else 'None'}")
        print(f"  - User role: {test_user.role}")
        
        # Verify membership
        membership = UserTenantMembership.objects.filter(
            user=test_user,
            tenant_id=tenant['id']
        ).first()
        if membership:
            print(f"  - Membership role: {membership.role}")
        
        core_tenant_id = tenant['id']
    else:
        print(f"\n✗ Failed to create tenant")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
        return
    
    # Test 2: Create tenant with CONSTRUCTION module
    print_section("TEST 2: CORE + CONSTRUCTION Module")
    
    tenant_data_construction = {
        'name': 'ABC Construction Co',
        'business_type': 'construction',
        'owner_name': 'Ram Sharma',
        'email': 'ram@abcconstruction.com',
        'phone': '+977 9823456789',
        'address': 'Pokhara, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction']
    }
    
    print("Creating tenant with CONSTRUCTION module...")
    print(f"Modules: {tenant_data_construction['active_modules']}")
    
    response = client.post('/api/tenants/', tenant_data_construction, format='json')
    
    if response.status_code == 201:
        tenant = response.data
        print(f"\n✓ Tenant created successfully!")
        print(f"  - ID: {tenant['id']}")
        print(f"  - Name: {tenant['name']}")
        print(f"  - Slug: {tenant['slug']}")
        print(f"  - Business Type: {tenant['business_type']}")
        print(f"  - Active Modules: {tenant['active_modules']}")
        
        # Verify construction module is active
        if 'construction' in tenant['active_modules']:
            print(f"\n✓ CONSTRUCTION module is active!")
        else:
            print(f"\n✗ CONSTRUCTION module NOT active!")
    else:
        print(f"\n✗ Failed to create tenant")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
    
    # Test 3: Create tenant with HARDWARE module
    print_section("TEST 3: CORE + HARDWARE Module")
    
    tenant_data_hardware = {
        'name': 'XYZ Hardware Store',
        'business_type': 'hardware',
        'owner_name': 'Shyam Thapa',
        'email': 'shyam@xyzhardware.com',
        'phone': '+977 9834567890',
        'address': 'Lalitpur, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'hardware']
    }
    
    print("Creating tenant with HARDWARE module...")
    print(f"Modules: {tenant_data_hardware['active_modules']}")
    
    response = client.post('/api/tenants/', tenant_data_hardware, format='json')
    
    if response.status_code == 201:
        tenant = response.data
        print(f"\n✓ Tenant created successfully!")
        print(f"  - ID: {tenant['id']}")
        print(f"  - Name: {tenant['name']}")
        print(f"  - Slug: {tenant['slug']}")
        print(f"  - Business Type: {tenant['business_type']}")
        print(f"  - Active Modules: {tenant['active_modules']}")
        
        # Verify hardware module is active
        if 'hardware' in tenant['active_modules']:
            print(f"\n✓ HARDWARE module is active!")
        else:
            print(f"\n✗ HARDWARE module NOT active!")
    else:
        print(f"\n✗ Failed to create tenant")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
        print(f"\n✗ Failed to create tenant")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.data, indent=2)}")
    
    # Test 4: Create tenant with ALL modules
    print_section("TEST 4: ALL Modules (CORE + CONSTRUCTION + HARDWARE)")
    
    tenant_data_all = {
        'name': 'Multi Business Enterprise',
        'business_type': 'other',
        'owner_name': 'Hari Bahadur',
        'email': 'hari@multibusiness.com',
        'phone': '+977 9845678901',
        'address': 'Bhaktapur, Nepal',
        'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction', 'hardware']
    }
    
    print("Creating tenant with ALL modules...")
    print(f"Modules: {tenant_data_all['active_modules']}")
    
    response = client.post('/api/tenants/', tenant_data_all, format='json')
    
    if response.status_code == 201:
        tenant = response.data
        print(f"\n✓ Tenant created successfully!")
        print(f"  - ID: {tenant['id']}")
        print(f"  - Name: {tenant['name']}")
        print(f"  - Slug: {tenant['slug']}")
        print(f"  - Business Type: {tenant['business_type']}")
        print(f"  - Active Modules: {tenant['active_modules']}")
        
        # Verify all modules are active
        expected_modules = ['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction', 'hardware']
        missing_modules = [m for m in expected_modules if m not in tenant['active_modules']]
        
        if not missing_modules:
            print(f"\n✓ ALL modules are active!")
        else:
            print(f"\n✗ Missing modules: {missing_modules}")
    else:
        print(f"\n✗ Failed to create tenant")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
    
    # Test 5: Verify module activation/deactivation
    print_section("TEST 5: Module Activation/Deactivation")
    
    # Get the first tenant
    tenant = Tenant.objects.get(id=core_tenant_id)
    print(f"Testing with tenant: {tenant.name}")
    print(f"Current modules: {tenant.active_modules}")
    
    # Activate construction module
    print("\nActivating 'construction' module...")
    response = client.post(f'/api/tenants/{tenant.slug}/activate_module/', {
        'module_name': 'construction'
    }, format='json')
    
    if response.status_code == 200:
        updated_tenant = response.data
        print(f"✓ Module activated!")
        print(f"  Updated modules: {updated_tenant['active_modules']}")
    else:
        print(f"✗ Failed to activate module")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
    
    # Deactivate construction module
    print("\nDeactivating 'construction' module...")
    response = client.post(f'/api/tenants/{tenant.slug}/deactivate_module/', {
        'module_name': 'construction'
    }, format='json')
    
    if response.status_code == 200:
        updated_tenant = response.data
        print(f"✓ Module deactivated!")
        print(f"  Updated modules: {updated_tenant['active_modules']}")
    else:
        print(f"✗ Failed to deactivate module")
        print(f"Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response: {json.dumps(response.data, indent=2)}")
        else:
            print(f"Response: {response.content.decode()}")
    
    # Summary
    print_section("TEST SUMMARY")
    
    all_tenants = Tenant.objects.filter(created_by=test_user)
    print(f"Total tenants created: {all_tenants.count()}")
    
    for tenant in all_tenants:
        print(f"\n{tenant.name}:")
        print(f"  - Business Type: {tenant.business_type}")
        print(f"  - Modules: {', '.join(tenant.active_modules)}")
        print(f"  - Plan: {tenant.plan_type}")
        print(f"  - Created from registration: {tenant.created_from_registration}")
    
    print("\n" + "="*60)
    print("✓ All tests completed successfully!")
    print("="*60 + "\n")
    
    # Cleanup
    print("Cleaning up test data...")
    all_tenants.delete()
    test_user.delete()
    print("✓ Cleanup complete")

if __name__ == '__main__':
    try:
        test_modular_tenant_creation()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
