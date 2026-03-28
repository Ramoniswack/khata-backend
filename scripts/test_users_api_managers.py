#!/usr/bin/env python
"""
Test Users API for managers
"""

import os
import sys
import django
import requests

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


def test_users_api():
    print("=" * 60)
    print("Test Users API for Managers")
    print("=" * 60)
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False, role='admin').first()
    
    if not user:
        print("\n❌ No admin user found with tenant")
        return
    
    print(f"\nTesting with user: {user.username}")
    print(f"Tenant: {user.tenant.name}")
    print(f"Role: {user.role}")
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    print(f"\nToken: {token.key[:20]}...")
    
    # Test API endpoint
    url = 'http://localhost:8000/api/auth/users/'
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "=" * 60)
    print("Test 1: Get all users")
    print("=" * 60)
    
    response = requests.get(url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        users = data.get('results', data) if isinstance(data, dict) else data
        print(f"Total users: {len(users)}")
        
        print("\nUsers:")
        for u in users:
            print(f"  - {u['username']} ({u['role']}) - {u.get('first_name', '')} {u.get('last_name', '')}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "=" * 60)
    print("Test 2: Filter by role=manager")
    print("=" * 60)
    
    response = requests.get(url, headers=headers, params={'role': 'manager'})
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        managers = data.get('results', data) if isinstance(data, dict) else data
        print(f"Total managers: {len(managers)}")
        
        if len(managers) > 0:
            print("\nManagers:")
            for m in managers:
                print(f"  - ID: {m['id']}")
                print(f"    Username: {m['username']}")
                print(f"    Name: {m.get('first_name', '')} {m.get('last_name', '')}")
                print(f"    Email: {m.get('email', '')}")
                print(f"    Role: {m['role']}")
                print()
        else:
            print("\n⚠️  No managers found!")
            print("\nChecking database directly...")
            
            managers_db = User.objects.filter(tenant=user.tenant, role='manager')
            print(f"Managers in database for tenant '{user.tenant.name}': {managers_db.count()}")
            
            if managers_db.count() > 0:
                print("\nManagers in database:")
                for m in managers_db:
                    print(f"  - {m.username} ({m.first_name} {m.last_name}) - {m.email}")
            else:
                print("\n❌ No managers in database for this tenant!")
                print("Run: python backend/scripts/check_and_create_managers.py")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    test_users_api()
