#!/usr/bin/env python
"""
Test script to create an invitation, accept it, and verify the user shows in the users list
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from users.models import User
from tenants.models import Tenant
from tenants.invitation_models import OrganizationInvitation
from tenants.membership_models import UserTenantMembership
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def test_invited_user_display():
    """Test that invited users show up in the users list"""
    
    print("🧪 Testing Invited Users Display")
    print("="*60)
    
    # Step 1: Get or create test users and tenant
    print("\n📝 Step 1: Setup test data")
    
    # Get Everest Builders tenant (has admin user)
    tenant = Tenant.objects.filter(name='Everest Builders').first()
    if not tenant:
        print("❌ Everest Builders tenant not found. Run seed_demo_data first.")
        return
    
    print(f"   Tenant: {tenant.name}")
    
    # Get the admin user
    admin_user = User.objects.filter(email='admin@everestbuilders.com.np').first()
    if not admin_user:
        print("❌ Admin user not found")
        return
    
    print(f"   Admin: {admin_user.email}")
    
    # Create or get a test user to invite
    invited_email = "testinvited@example.com"
    invited_user, created = User.objects.get_or_create(
        email=invited_email,
        defaults={
            'username': 'testinvited',
            'first_name': 'Test',
            'last_name': 'Invited',
        }
    )
    if created:
        invited_user.set_password('test123')
        invited_user.save()
        print(f"   Created invited user: {invited_email}")
    else:
        print(f"   Using existing user: {invited_email}")
    
    # Step 2: Login as admin
    print(f"\n🔐 Step 2: Login as admin")
    login_response = requests.post(
        f"{API_BASE}/auth/login/",
        json={"email": admin_user.email, "password": "demo123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    admin_token = login_response.json()['access']
    print("✅ Admin logged in")
    
    # Step 3: Check current users count
    print(f"\n📊 Step 3: Check current users")
    headers = {"Authorization": f"Bearer {admin_token}"}
    users_response = requests.get(f"{API_BASE}/auth/users/", headers=headers)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to fetch users: {users_response.text}")
        return
    
    users_data = users_response.json()
    current_users = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
    print(f"   Current users count: {len(current_users)}")
    for user in current_users:
        print(f"      - {user['email']} ({user['role']})")
    
    # Step 4: Send invitation
    print(f"\n📧 Step 4: Send invitation to {invited_email}")
    
    # Check if invitation already exists
    existing_invitation = OrganizationInvitation.objects.filter(
        tenant=tenant,
        invited_user=invited_user,
        status='pending'
    ).first()
    
    if existing_invitation:
        print(f"   Using existing invitation (ID: {existing_invitation.id})")
        invitation_id = existing_invitation.id
    else:
        invite_response = requests.post(
            f"{API_BASE}/tenants/invitations/",
            headers=headers,
            json={
                "invited_user_email": invited_email,
                "role": "manager",
                "message": "Test invitation"
            }
        )
        
        if invite_response.status_code not in [200, 201]:
            print(f"❌ Failed to send invitation: {invite_response.text}")
            return
        
        invitation_id = invite_response.json()['id']
        print(f"✅ Invitation sent (ID: {invitation_id})")
    
    # Step 5: Accept invitation
    print(f"\n✅ Step 5: Accept invitation")
    
    # Login as invited user
    invited_login_response = requests.post(
        f"{API_BASE}/auth/login/",
        json={"email": invited_email, "password": "test123"}
    )
    
    if invited_login_response.status_code != 200:
        print(f"❌ Invited user login failed: {invited_login_response.text}")
        return
    
    invited_token = invited_login_response.json()['access']
    print(f"   Invited user logged in")
    
    # Accept the invitation
    invited_headers = {"Authorization": f"Bearer {invited_token}"}
    accept_response = requests.post(
        f"{API_BASE}/tenants/invitations/{invitation_id}/respond/",
        headers=invited_headers,
        json={"action": "accept"}
    )
    
    if accept_response.status_code != 200:
        print(f"❌ Failed to accept invitation: {accept_response.text}")
        # Check if already accepted
        membership = UserTenantMembership.objects.filter(
            user=invited_user,
            tenant=tenant
        ).first()
        if membership:
            print(f"   ℹ️  User already has membership (role: {membership.role})")
        else:
            return
    else:
        print(f"✅ Invitation accepted")
    
    # Step 6: Verify membership was created
    print(f"\n🔍 Step 6: Verify membership")
    membership = UserTenantMembership.objects.filter(
        user=invited_user,
        tenant=tenant
    ).first()
    
    if membership:
        print(f"✅ Membership exists: {membership.user.email} -> {membership.tenant.name} ({membership.role})")
    else:
        print(f"❌ No membership found!")
        return
    
    # Step 7: Check users list again (as admin)
    print(f"\n📊 Step 7: Check users list after invitation accepted")
    users_response2 = requests.get(f"{API_BASE}/auth/users/", headers=headers)
    
    if users_response2.status_code != 200:
        print(f"❌ Failed to fetch users: {users_response2.text}")
        return
    
    users_data2 = users_response2.json()
    updated_users = users_data2.get('results', users_data2) if isinstance(users_data2, dict) else users_data2
    print(f"   Updated users count: {len(updated_users)}")
    
    invited_user_found = False
    for user in updated_users:
        print(f"      - {user['email']} ({user['role']})")
        if user['email'] == invited_email:
            invited_user_found = True
    
    # Step 8: Results
    print(f"\n" + "="*60)
    print(f"📋 RESULTS:")
    print(f"   Before invitation: {len(current_users)} users")
    print(f"   After invitation: {len(updated_users)} users")
    print(f"   Invited user in list: {'✅ YES' if invited_user_found else '❌ NO'}")
    
    if invited_user_found:
        print(f"\n✅ SUCCESS: Invited users are showing in the users list!")
    else:
        print(f"\n❌ ISSUE: Invited user is NOT showing in the users list")
        print(f"   This means the backend fix needs to be applied")


if __name__ == "__main__":
    test_invited_user_display()
