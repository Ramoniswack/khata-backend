#!/usr/bin/env python
"""
Test creating an invitation via API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from tenants.views import OrganizationInvitationViewSet
from users.models import User
from rest_framework.test import force_authenticate
import json

def test_create_invitation():
    print("=" * 80)
    print("TESTING INVITATION CREATION")
    print("=" * 80)
    
    # Get the inviter (user1@test.com)
    try:
        inviter = User.objects.get(email='user1@test.com')
        print(f"\n✓ Inviter: {inviter.email}")
        print(f"  - Tenant: {inviter.tenant}")
        print(f"  - Role: {inviter.role}")
    except User.DoesNotExist:
        print("\n✗ user1@test.com not found!")
        return
    
    if not inviter.tenant:
        print("\n✗ Inviter has no tenant!")
        return
    
    # Test with an existing user
    print("\n" + "=" * 80)
    print("TEST 1: Invite existing user (user4@test.com)")
    print("=" * 80)
    
    factory = RequestFactory()
    data = {
        'invited_user_email': 'user4@test.com',
        'role': 'manager',
        'message': 'Join our team!'
    }
    
    request = factory.post('/api/tenants/invitations/', 
                          data=json.dumps(data),
                          content_type='application/json')
    force_authenticate(request, user=inviter)
    
    viewset = OrganizationInvitationViewSet.as_view({'post': 'create'})
    
    try:
        response = viewset(request)
        print(f"\n✓ Response status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✓ SUCCESS! Invitation created")
            print(f"  Response data: {response.data}")
        else:
            print(f"✗ FAILED with status {response.status_code}")
            print(f"  Response data: {response.data}")
    except Exception as e:
        print(f"\n✗ EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test with non-existing user
    print("\n" + "=" * 80)
    print("TEST 2: Invite non-existing user (nonexistent@test.com)")
    print("=" * 80)
    
    data2 = {
        'invited_user_email': 'nonexistent@test.com',
        'role': 'viewer',
        'message': 'Please join!'
    }
    
    request2 = factory.post('/api/tenants/invitations/', 
                           data=json.dumps(data2),
                           content_type='application/json')
    force_authenticate(request2, user=inviter)
    
    try:
        response2 = viewset(request2)
        print(f"\n✓ Response status: {response2.status_code}")
        
        if response2.status_code == 400:
            print(f"✓ EXPECTED 400 ERROR")
            print(f"  Response data: {response2.data}")
        else:
            print(f"✗ Unexpected status {response2.status_code}")
            print(f"  Response data: {response2.data}")
    except Exception as e:
        print(f"\n✗ EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_create_invitation()
