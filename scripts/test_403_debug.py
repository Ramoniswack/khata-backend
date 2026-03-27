#!/usr/bin/env python
"""
Test script to debug 403 error on user profile endpoint
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import requests

def test_profile_access():
    """Test accessing the profile endpoint with different scenarios"""
    
    print("=" * 80)
    print("TESTING USER PROFILE ACCESS - 403 ERROR DEBUG")
    print("=" * 80)
    
    # Get a test user
    user = User.objects.filter(is_active=True).first()
    
    if not user:
        print("\n❌ No active users found. Please create a user first.")
        return
    
    print(f"\n✓ Testing with user: {user.email}")
    print(f"  - Username: {user.username}")
    print(f"  - Has tenant: {user.tenant is not None}")
    if user.tenant:
        print(f"  - Tenant: {user.tenant.name} (slug: {user.tenant.slug})")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f"\n✓ Generated JWT token")
    print(f"  - Token (first 50 chars): {access_token[:50]}...")
    
    # Test the profile endpoint
    base_url = "http://127.0.0.1:8000"
    profile_url = f"{base_url}/api/auth/profile/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Making request to: {profile_url}")
    print(f"   Headers: Authorization: Bearer {access_token[:30]}...")
    
    try:
        response = requests.get(profile_url, headers=headers)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Profile endpoint is working")
            data = response.json()
            print(f"\n📄 Response data:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Email: {data.get('email')}")
            print(f"   - Username: {data.get('username')}")
            print(f"   - Tenant: {data.get('tenant')}")
        elif response.status_code == 403:
            print("❌ 403 FORBIDDEN ERROR")
            print(f"\n📄 Response body:")
            print(response.text)
            
            # Check common causes
            print("\n🔍 Checking common causes:")
            
            # 1. Check if user is active
            if not user.is_active:
                print("   ❌ User is not active")
            else:
                print("   ✓ User is active")
            
            # 2. Check if token is valid
            print("   ✓ Token was just generated, should be valid")
            
            # 3. Check authentication backend
            from django.conf import settings
            print(f"   ✓ Authentication backends: {settings.AUTHENTICATION_BACKENDS}")
            
            # 4. Check REST framework settings
            print(f"   ✓ DRF auth classes: {settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES')}")
            print(f"   ✓ DRF permission classes: {settings.REST_FRAMEWORK.get('DEFAULT_PERMISSION_CLASSES')}")
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"\n📄 Response body:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("   The Django server is not running!")
        print("   Please start the server with: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    # Test with email login
    print("\n" + "=" * 80)
    print("TESTING EMAIL LOGIN")
    print("=" * 80)
    
    login_url = f"{base_url}/api/auth/login/"
    login_data = {
        "email": user.email,
        "password": "test123"  # You may need to adjust this
    }
    
    print(f"\n📡 Making login request to: {login_url}")
    print(f"   Data: {login_data}")
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ LOGIN SUCCESS!")
            data = response.json()
            print(f"\n📄 Response contains:")
            print(f"   - access token: {'access' in data}")
            print(f"   - refresh token: {'refresh' in data}")
            
            # Now test profile with this token
            new_access_token = data.get('access')
            if new_access_token:
                print(f"\n📡 Testing profile with login token...")
                headers = {
                    "Authorization": f"Bearer {new_access_token}",
                    "Content-Type": "application/json"
                }
                response = requests.get(profile_url, headers=headers)
                print(f"📥 Profile Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Profile access works with login token!")
                else:
                    print(f"❌ Profile access failed: {response.status_code}")
                    print(response.text)
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            print("\n💡 Note: The test password might be wrong.")
            print("   Try logging in through the frontend first.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("""
    If you're getting 403 errors:
    
    1. Clear browser localStorage:
       - Open browser DevTools (F12)
       - Go to Application/Storage tab
       - Clear localStorage
       - Try logging in again
    
    2. Check token expiration:
       - Access tokens expire after 1 hour by default
       - Refresh tokens expire after 7 days
       - Old tokens will cause 403 errors
    
    3. Verify the server is running:
       - Make sure Django server is running on port 8000
       - Check for any errors in the server console
    
    4. Check CORS settings:
       - Verify CORS_ALLOWED_ORIGINS includes your frontend URL
       - Check for CORS errors in browser console
    
    5. Try a fresh login:
       - Go to http://localhost:3000/auth/login
       - Login with your credentials
       - This will generate fresh tokens
    """)

if __name__ == '__main__':
    test_profile_access()
