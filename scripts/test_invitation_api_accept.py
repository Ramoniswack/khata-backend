#!/usr/bin/env python
"""
Test the invitation accept API endpoint to reproduce the 500 error
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
from tenants.invitation_models import OrganizationInvitation
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

User = get_user_model()

def test_api_accept():
    """Test accepting invitation via API"""
    print("\n" + "="*60)
    print("TESTING INVITATION ACCEPT VIA API")
    print("="*60)
    
    # Add testserver to ALLOWED_HOSTS temporarily
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
    
    # Get users
    inviter = User.objects.filter(tenant__isnull=False).first()
    invitee = User.objects.exclude(id=inviter.id).first()
    
    if not inviter or not invitee:
        print("❌ Need at least 2 users")
        return False
    
    tenant = inviter.tenant
    
    print(f"\n✓ Inviter: {inviter.email}")
    print(f"✓ Invitee: {invitee.email}")
    print(f"✓ Tenant: {tenant.name}")
    
    # Check for existing pending invitation
    invitation = OrganizationInvitation.objects.filter(
        tenant=tenant,
        invited_user=invitee,
        status='pending'
    ).first()
    
    if invitation:
        print(f"\n✓ Using existing pending invitation (ID: {invitation.id})")
    else:
        # Create a new pending invitation
        print("\n📧 Creating new invitation...")
        invitation = OrganizationInvitation.objects.create(
            tenant=tenant,
            invited_user=invitee,
            invited_by=inviter,
            role='supervisor',
            message='Test invitation',
            expires_at=timezone.now() + timedelta(days=7)
        )
        print(f"✓ Invitation created (ID: {invitation.id})")
    
    # Get JWT token for invitee
    refresh = RefreshToken.for_user(invitee)
    access_token = str(refresh.access_token)
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test the accept endpoint
    print(f"\n🔄 Calling API: POST /api/tenants/invitations/{invitation.id}/respond/")
    print(f"   Data: {{'action': 'accept'}}")
    
    response = client.post(
        f'/api/tenants/invitations/{invitation.id}/respond/',
        {'action': 'accept'},
        format='json'
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    if hasattr(response, 'data'):
        print(f"📊 Response Data: {response.data}")
    else:
        print(f"📊 Response Content: {response.content.decode()}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Invitation accepted via API")
        
        # Refresh invitation
        invitation.refresh_from_db()
        print(f"\nInvitation status: {invitation.status}")
        
        return True
    else:
        print(f"\n❌ FAILED! Status code: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Error: {response.data}")
        return False

if __name__ == '__main__':
    success = test_api_accept()
    sys.exit(0 if success else 1)
