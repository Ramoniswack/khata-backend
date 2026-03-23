"""
Test tenant creation and user assignment flow
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from tenants.views import TenantViewSet
from users.views import UserViewSet

User = get_user_model()

def test_tenant_creation_flow():
    """Test the complete tenant creation and user assignment flow"""
    
    # Create a test user without tenant
    test_username = "testuser_flow"
    test_email = "testuser_flow@example.com"
    
    # Clean up if exists
    User.objects.filter(username=test_username).delete()
    User.objects.filter(email=test_email).delete()
    
    user = User.objects.create_user(
        username=test_username,
        email=test_email,
        password="testpass123",
        first_name="Test",
        last_name="User",
        tenant=None  # No tenant initially
    )
    
    print(f"✅ Created user: {user.email}")
    print(f"   - Has tenant: {user.tenant is not None}")
    print(f"   - Role: {user.role}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Create tenant
    print("\n" + "="*60)
    print("TEST 1: Create Tenant")
    print("="*60)
    
    tenant_data = {
        'name': 'Test Organization Flow',
        'business_type': 'construction',
        'active_modules': ['inventory', 'sales', 'purchase']
    }
    
    request = factory.post(
        '/api/tenants/',
        data=json.dumps(tenant_data),
        content_type='application/json'
    )
    force_authenticate(request, user=user)
    
    view = TenantViewSet.as_view({'post': 'create'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.data
        print("✅ Tenant created successfully:")
        print(f"   Response data: {data}")
        
        # Refresh user from database
        user.refresh_from_db()
        print(f"\n✅ User updated:")
        print(f"   - Has tenant: {user.tenant is not None}")
        print(f"   - Tenant name: {user.tenant.name if user.tenant else 'None'}")
        print(f"   - Role: {user.role}")
        
        # Test 2: Get user profile
        print("\n" + "="*60)
        print("TEST 2: Get User Profile")
        print("="*60)
        
        request = factory.get('/api/auth/profile/')
        force_authenticate(request, user=user)
        
        view = UserViewSet.as_view({'get': 'profile'})
        response = view(request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.data
            print("✅ Profile retrieved:")
            print(f"   - Username: {profile['username']}")
            print(f"   - Role: {profile['role']}")
            print(f"   - Has tenant: {profile['tenant'] is not None}")
            if profile['tenant']:
                print(f"   - Tenant name: {profile['tenant']['name']}")
                print(f"   - Tenant slug: {profile['tenant']['slug']}")
        else:
            print(f"❌ Error: {response.data}")
        
        # Test 3: List tenants (should see only their tenant)
        print("\n" + "="*60)
        print("TEST 3: List Tenants")
        print("="*60)
        
        request = factory.get('/api/tenants/')
        force_authenticate(request, user=user)
        
        view = TenantViewSet.as_view({'get': 'list'})
        response = view(request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            tenants = response.data
            if isinstance(tenants, dict) and 'results' in tenants:
                tenants = tenants['results']
            print(f"✅ Found {len(tenants)} tenant(s)")
            for t in tenants:
                print(f"   - {t['name']} ({t['slug']})")
        else:
            print(f"❌ Error: {response.data}")
        
    else:
        print(f"❌ Error: {response.data}")
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    if user.tenant:
        tenant_name = user.tenant.name
        user.tenant.delete()
        print(f"✅ Deleted tenant: {tenant_name}")
    
    user.delete()
    print(f"✅ Deleted user: {test_email}")
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_tenant_creation_flow()
