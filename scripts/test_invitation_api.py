#!/usr/bin/env python
"""
Test invitation API endpoints
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
import requests

User = get_user_model()

def test_invitation_api():
    print("=" * 60)
    print("Testing Invitation API Endpoints")
    print("=" * 60)
    
    # Get or create admin user with tenant
    admin_user = User.objects.filter(email="admin@khata.com").first()
    if not admin_user:
        print("❌ Admin user not found")
        return
    
    if not admin_user.tenant:
        print("❌ Admin user has no tenant")
        return
    
    print(f"✅ Using admin: {admin_user.email}")
    print(f"✅ Tenant: {admin_user.tenant.name}")
    
    # Get or create regular user without tenant
    regular_user = User.objects.filter(email="invitetest@example.com").first()
    if not regular_user:
        regular_user = User.objects.create_user(
            username="invitetest",
            email="invitetest@example.com",
            password="test123",
            first_name="Invite",
            last_name="Test",
            role="viewer"
        )
        print(f"✅ Created test user: {regular_user.email}")
    else:
        # Make sure user has no tenant
        regular_user.tenant = None
        regular_user.save()
        print(f"✅ Using test user: {regular_user.email}")
    
    # Login as admin
    login_url = "http://localhost:8000/api/auth/login/"
    login_data = {"email": admin_user.email, "password": "admin123"}
    
    print(f"\n📡 Logging in as admin...")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json()['access']
    print(f"✅ Login successful")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test creating invitation
    print(f"\n📡 Creating invitation...")
    invitation_url = "http://localhost:8000/api/tenants/invitations/"
    invitation_data = {
        "invited_user_email": regular_user.email,
        "role": "manager",
        "message": "Welcome to our team!"
    }
    
    response = requests.post(invitation_url, json=invitation_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print(f"✅ Invitation created successfully!")
        invitation = response.json()
        print(f"   Invitation ID: {invitation['id']}")
        print(f"   Status: {invitation['status']}")
    else:
        print(f"❌ Failed to create invitation")
    
    # Test getting invitations
    print(f"\n📡 Getting sent invitations...")
    response = requests.get(f"{invitation_url}sent/", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        invitations = response.json()
        print(f"✅ Found {len(invitations)} sent invitations")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_invitation_api()
