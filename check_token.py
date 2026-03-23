#!/usr/bin/env python
"""
Script to decode and check JWT token claims
Usage: python check_token.py <your_access_token>
"""
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from rest_framework_simplejwt.tokens import AccessToken

def check_token(token_string):
    try:
        token = AccessToken(token_string)
        print("\n=== JWT Token Claims ===")
        print(f"User ID: {token.get('user_id', 'Not found')}")
        print(f"Username: {token.get('username', 'Not found')}")
        print(f"Role: {token.get('role', 'Not found')}")
        print(f"Tenant ID: {token.get('tenant_id', 'Not found')}")
        print(f"Tenant Slug: {token.get('tenant_slug', 'Not found')}")
        print(f"Tenant Name: {token.get('tenant_name', 'Not found')}")
        
        print("\n=== Analysis ===")
        if token.get('tenant_id') is None:
            print("❌ Token does NOT have tenant information")
            print("⚠️  You need to log out and log back in to get a fresh token")
        else:
            print("✓ Token has tenant information")
            print("✓ Token is valid for tenant-specific operations")
        
    except Exception as e:
        print(f"Error decoding token: {e}")
        print("\nMake sure you're using a valid access token from localStorage")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_token.py <your_access_token>")
        print("\nTo get your token:")
        print("1. Open browser DevTools (F12)")
        print("2. Go to Console tab")
        print("3. Type: localStorage.getItem('access_token')")
        print("4. Copy the token (without quotes)")
        print("5. Run: python check_token.py <paste_token_here>")
    else:
        check_token(sys.argv[1])
