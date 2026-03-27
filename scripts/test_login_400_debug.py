#!/usr/bin/env python
"""
Test script to debug 400 error on login endpoint
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User

def test_login_endpoint():
    """Test the login endpoint with different payloads"""
    
    print("=" * 80)
    print("TESTING LOGIN ENDPOINT - 400 ERROR DEBUG")
    print("=" * 80)
    
    # Get a test user
    user = User.objects.filter(is_active=True).first()
    
    if not user:
        print("\n❌ No active users found. Creating test user...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123',
            first_name='Test',
            last_name='User'
        )
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"\n✓ Using existing user: {user.email}")
        print(f"  - Username: {user.username}")
        print(f"  - Has tenant: {user.tenant is not None}")
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/auth/login/"
    
    # Test 1: Login with email and password (correct format)
    print("\n" + "=" * 80)
    print("TEST 1: Login with email and password")
    print("=" * 80)
    
    payload1 = {
        "email": user.email,
        "password": "test123"
    }
    
    print(f"\n📡 POST {login_url}")
    print(f"📦 Payload: {json.dumps(payload1, indent=2)}")
    
    try:
        response = requests.post(login_url, json=payload1)
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Login with email works")
        elif response.status_code == 400:
            print("\n❌ 400 BAD REQUEST")
            print("This means the serializer rejected the input")
        elif response.status_code == 401:
            print("\n❌ 401 UNAUTHORIZED")
            print("This means credentials are invalid")
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR - Django server is not running!")
        print("Please start the server with: python manage.py runserver")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return
    
    # Test 2: Login with username and password (old format)
    print("\n" + "=" * 80)
    print("TEST 2: Login with username and password (old format)")
    print("=" * 80)
    
    payload2 = {
        "username": user.username,
        "password": "test123"
    }
    
    print(f"\n📡 POST {login_url}")
    print(f"📦 Payload: {json.dumps(payload2, indent=2)}")
    
    try:
        response = requests.post(login_url, json=payload2)
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Login with username works")
        elif response.status_code == 400:
            print("\n❌ 400 BAD REQUEST")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    # Test 3: Check what fields the serializer expects
    print("\n" + "=" * 80)
    print("SERIALIZER CONFIGURATION")
    print("=" * 80)
    
    from users.serializers import CustomTokenObtainPairSerializer
    
    print(f"\n✓ Serializer class: CustomTokenObtainPairSerializer")
    print(f"✓ Username field: {CustomTokenObtainPairSerializer.username_field}")
    
    # Check if the serializer has the right fields
    serializer = CustomTokenObtainPairSerializer()
    print(f"✓ Serializer fields: {list(serializer.fields.keys())}")
    
    # Test 4: Try to create a user and test login
    print("\n" + "=" * 80)
    print("TEST 4: Create fresh user and test login")
    print("=" * 80)
    
    # Create a fresh test user
    test_email = "freshuser@example.com"
    test_password = "testpass123"
    
    # Delete if exists
    User.objects.filter(email=test_email).delete()
    
    fresh_user = User.objects.create_user(
        username='freshuser',
        email=test_email,
        password=test_password,
        first_name='Fresh',
        last_name='User'
    )
    
    print(f"\n✓ Created fresh user:")
    print(f"  - Email: {fresh_user.email}")
    print(f"  - Username: {fresh_user.username}")
    print(f"  - Password: {test_password}")
    
    payload3 = {
        "email": test_email,
        "password": test_password
    }
    
    print(f"\n📡 POST {login_url}")
    print(f"📦 Payload: {json.dumps(payload3, indent=2)}")
    
    try:
        response = requests.post(login_url, json=payload3)
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Fresh user login works")
            data = response.json()
            print(f"\n📄 Response contains:")
            print(f"  - access token: {'access' in data}")
            print(f"  - refresh token: {'refresh' in data}")
            print(f"  - user data: {'user' in data}")
            if 'user' in data:
                print(f"  - user email: {data['user'].get('email')}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"📄 Response Body:")
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("""
    If you're getting 400 errors on login:
    
    1. Check the payload format:
       - Should be: {"email": "user@example.com", "password": "password"}
       - NOT: {"username": "username", "password": "password"}
    
    2. Verify the serializer configuration:
       - CustomTokenObtainPairSerializer.username_field should be 'email'
       - The serializer should accept 'email' field
    
    3. Check authentication backend:
       - EmailBackend should be in AUTHENTICATION_BACKENDS
       - It should authenticate using email
    
    4. Test with a known user:
       - Use the fresh user created above
       - Email: freshuser@example.com
       - Password: testpass123
    
    5. Check frontend payload:
       - Open browser DevTools
       - Go to Network tab
       - Look at the login request payload
       - Verify it's sending {"email": "...", "password": "..."}
    """)

if __name__ == '__main__':
    test_login_endpoint()
