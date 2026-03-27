#!/usr/bin/env python
"""
Test tenant deletion via API to simulate the frontend request
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_tenant_delete_api():
    print("=" * 60)
    print("Testing Tenant Deletion via API")
    print("=" * 60)
    
    # Create a test user
    print("\n1. Creating test user...")
    user = User.objects.create_user(
        username="test_api_user",
        email="test_api@example.com",
        password="test123",
        role="admin"
    )
    print(f"✅ Created user: {user.email}")
    
    # Create a test tenant
    print("\n2. Creating test tenant...")
    tenant = Tenant.objects.create(
        name="Test API Delete Tenant",
        business_type="construction",
        created_by=user,
        created_from_registration=False
    )
    user.tenant = tenant
    user.save()
    print(f"✅ Created tenant: {tenant.name} (slug: {tenant.slug})")
    print(f"   User assigned to tenant: {user.tenant.name}")
    
    # Create another user in the same tenant
    print("\n3. Creating another user in the tenant...")
    user2 = User.objects.create_user(
        username="test_api_user2",
        email="test_api2@example.com",
        password="test123",
        tenant=tenant,
        role="manager"
    )
    print(f"✅ Created user2: {user2.email} (tenant: {user2.tenant.name})")
    
    # Get JWT token
    print("\n4. Getting JWT token...")
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    print(f"✅ Got JWT token")
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Try to delete the tenant via API
    print(f"\n5. Attempting to delete tenant via API...")
    print(f"   DELETE /api/tenants/{tenant.slug}/")
    
    response = client.delete(f'/api/tenants/{tenant.slug}/')
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Tenant deleted successfully")
        
        # Check if users still exist
        user.refresh_from_db()
        user2.refresh_from_db()
        print(f"   User1 tenant: {user.tenant}")
        print(f"   User2 tenant: {user2.tenant}")
        
    else:
        print(f"❌ Error deleting tenant")
        print(f"   Response: {response.data if hasattr(response, 'data') else response.content}")
    
    # Cleanup
    print("\n6. Cleanup...")
    try:
        User.objects.filter(username__in=["test_api_user", "test_api_user2"]).delete()
        if Tenant.objects.filter(slug=tenant.slug).exists():
            Tenant.objects.filter(slug=tenant.slug).delete()
        print("✅ Cleaned up test data")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_tenant_delete_api()
