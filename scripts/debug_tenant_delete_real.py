#!/usr/bin/env python
"""
Debug actual tenant deletion issue from frontend
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.views import TenantViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def debug_delete():
    print("=" * 60)
    print("Debugging Tenant Deletion Issue")
    print("=" * 60)
    
    # Get a real user and tenant from the database
    print("\n1. Finding existing user and tenant...")
    
    # Find a user with a tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found. Creating test data...")
        user = User.objects.create_user(
            username="debug_user",
            email="debug@test.com",
            password="test123",
            role="admin"
        )
        tenant = Tenant.objects.create(
            name="Debug Tenant",
            business_type="construction",
            created_by=user,
            created_from_registration=False
        )
        user.tenant = tenant
        user.save()
    else:
        tenant = user.tenant
    
    print(f"✅ User: {user.email} (ID: {user.id})")
    print(f"✅ Tenant: {tenant.name} (slug: {tenant.slug}, ID: {tenant.id})")
    print(f"   Created by: {tenant.created_by}")
    print(f"   Created from registration: {tenant.created_from_registration}")
    
    # Check queryset filtering
    print("\n2. Checking queryset filtering...")
    factory = APIRequestFactory()
    request = factory.delete(f'/api/tenants/{tenant.slug}/')
    force_authenticate(request, user=user)
    
    viewset = TenantViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    viewset.kwargs = {'slug': tenant.slug}
    
    queryset = viewset.get_queryset()
    print(f"   Queryset count: {queryset.count()}")
    print(f"   Tenant in queryset: {queryset.filter(slug=tenant.slug).exists()}")
    
    if not queryset.filter(slug=tenant.slug).exists():
        print("❌ ISSUE FOUND: Tenant not in queryset!")
        print(f"   Queryset filters: created_by={user.id}, created_from_registration=False")
        print(f"   Tenant created_by: {tenant.created_by_id}")
        print(f"   Tenant created_from_registration: {tenant.created_from_registration}")
        
        # Check if user is the creator
        if tenant.created_by != user:
            print(f"   ⚠️  User is NOT the creator of this tenant!")
            print(f"   Tenant creator: {tenant.created_by}")
        
        # Check created_from_registration flag
        if tenant.created_from_registration:
            print(f"   ⚠️  Tenant was created from registration (hidden from ERP)")
    
    # Try to get the object
    print("\n3. Attempting to get object...")
    try:
        obj = viewset.get_object()
        print(f"✅ Got object: {obj}")
    except Exception as e:
        print(f"❌ Error getting object: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Try to delete
    print("\n4. Attempting to delete...")
    try:
        response = viewset.destroy(request, slug=tenant.slug)
        print(f"✅ Delete response status: {response.status_code}")
        print(f"   Response data: {response.data if hasattr(response, 'data') else 'No data'}")
    except Exception as e:
        print(f"❌ Error deleting: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Debug Complete")
    print("=" * 60)

if __name__ == "__main__":
    debug_delete()
