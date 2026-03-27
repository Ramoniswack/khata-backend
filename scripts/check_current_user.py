#!/usr/bin/env python
"""
Check the currently logged-in user's details
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_user(email):
    print("=" * 70)
    print("USER DETAILS CHECK")
    print("=" * 70)
    
    try:
        user = User.objects.get(email=email)
        
        print(f"\n✅ Found user: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role}")
        print(f"   Is Admin: {user.is_admin}")
        print(f"   Tenant: {user.tenant.name if user.tenant else 'None'}")
        print(f"   Tenant Slug: {user.tenant.slug if user.tenant else 'None'}")
        
        if user.tenant:
            print(f"\n   Organization Details:")
            print(f"   - Name: {user.tenant.name}")
            print(f"   - Slug: {user.tenant.slug}")
            print(f"   - Business Type: {user.tenant.business_type}")
            print(f"   - Created By: {user.tenant.created_by.email if user.tenant.created_by else 'None'}")
            print(f"   - Created from Registration: {user.tenant.created_from_registration}")
            print(f"   - Is Active: {user.tenant.is_active}")
            
            # Check if user is creator
            if user.tenant.created_by == user:
                print(f"\n   👑 You are the CREATOR of this organization")
            else:
                print(f"\n   ℹ️  You are a MEMBER of this organization")
            
            # Check if can delete
            if user.is_admin and user.tenant:
                print(f"\n   ✅ You CAN delete this organization")
            else:
                print(f"\n   ❌ You CANNOT delete this organization")
                if not user.is_admin:
                    print(f"      Reason: You're not an admin (role: {user.role})")
                if not user.tenant:
                    print(f"      Reason: You don't have a tenant assigned")
        else:
            print(f"\n   ⚠️  You don't have any organization assigned")
            print(f"      You need to create or join an organization first")
        
    except User.DoesNotExist:
        print(f"\n❌ User with email '{email}' not found")
        print(f"\nAvailable users:")
        for u in User.objects.all()[:10]:
            print(f"   - {u.email} (role: {u.role})")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        # Get the most recently created user
        user = User.objects.order_by('-date_joined').first()
        if user:
            email = user.email
            print(f"No email provided, checking most recent user: {email}\n")
        else:
            print("No users found in database")
            sys.exit(1)
    
    check_user(email)
