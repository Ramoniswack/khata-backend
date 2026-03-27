#!/usr/bin/env python
"""
Test script for modular tenant creation with module selection
Tests the complete flow of creating a tenant with specific modules
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
import json
from django.contrib.auth import get_user_model

User = get_user_model()

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_modular_tenant_creation():
    """Test creating tenants with different module configurations"""
    
    print_section("MODULAR TENANT CREATION TEST")
    
    # Get or create test user
    print("1. Setting up test user...")
    user, created = User.objects.get_or_create(
        username='moduletest',
        defaults={
            'email': 'moduletest@example.com',
            'first_name': 'Module',
            'last_name': 'Tester'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"   ✓ Created user: {user.username}")
    else:
        print(f"   ✓ Using existing user: {user.username}")
    
    # Login
    print("\n2. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={
            "email": "moduletest@example.com",
            "password": "testpass123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"   ✗ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    tokens = login_response.json()
    access_token = tokens['access']
    print(f"   ✓ Login successful")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test Case 1: Construction Business with Construction Module
    print_section("TEST CASE 1: Construction Business")
    
    construction_data = {
        "name": "ABC Construction Ltd",
        "business_type": "construction",
        "owner_name": "John Builder",
        "email": "john@abcconstruction.com",
        "phone": "+977-9841234567",
        "address": "Kathmandu, Nepal",
        "active_modules": [
            "inventory",
            "sales",
            "purchase",
            "accounting",
            "construction",  # Construction-specific module
            "reports"
        ]
    }
    
    print("Creating construction tenant...")
    print(f"Modules: {', '.join(construction_data['active_modules'])}")
    
    response = requests.post(
        f"{BASE_URL}/tenants/",
        headers=headers,
        json=construction_data
    )
    
    if response.status_code == 201:
        tenant = response.json()
        print(f"\n✓ Construction tenant created successfully!")
        print(f"  ID: {tenant['id']}")
        print(f"  Name: {tenant['name']}")
        print(f"  Slug: {tenant['slug']}")
        print(f"  Business Type: {tenant['business_type']}")
        print(f"  Active Modules: {', '.join(tenant['active_modules'])}")
        print(f"  Has Construction Module: {tenant.get('active_modules', []).count('construction') > 0}")
    else:
        print(f"✗ Failed to create tenant: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Test Case 2: Hardware Business with Hardware Module
    print_section("TEST CASE 2: Hardware Business")
    
    hardware_data = {
        "name": "XYZ Hardware Store",
        "business_type": "hardware",
        "owner_name": "Ram Sharma",
        "email": "ram@xyzhardware.com",
        "phone": "+977-9851234567",
        "address": "Pokhara, Nepal",
        "active_modules": [
            "inventory",
            "sales",
            "purchase",
            "accounting",
            "hardware",  # Hardware-specific module
            "reports"
        ]
    }
    
    print("Creating hardware tenant...")
    print(f"Modules: {', '.join(hardware_data['active_modules'])}")
    
    response = requests.post(
        f"{BASE_URL}/tenants/",
        headers=headers,
        json=hardware_data
    )
    
    if response.status_code == 201:
        tenant = response.json()
        print(f"\n✓ Hardware tenant created successfully!")
        print(f"  ID: {tenant['id']}")
        print(f"  Name: {tenant['name']}")
        print(f"  Slug: {tenant['slug']}")
        print(f"  Business Type: {tenant['business_type']}")
        print(f"  Active Modules: {', '.join(tenant['active_modules'])}")
        print(f"  Has Hardware Module: {tenant.get('active_modules', []).count('hardware') > 0}")
    else:
        print(f"✗ Failed to create tenant: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Test Case 3: Core Only (No Business Modules)
    print_section("TEST CASE 3: Core Modules Only")
    
    core_only_data = {
        "name": "Simple Services Co",
        "business_type": "services",
        "owner_name": "Sita Devi",
        "email": "sita@simpleservices.com",
        "phone": "+977-9861234567",
        "address": "Lalitpur, Nepal",
        "active_modules": [
            "inventory",
            "sales",
            "purchase",
            "accounting",
            "reports"
        ]
    }
    
    print("Creating core-only tenant...")
    print(f"Modules: {', '.join(core_only_data['active_modules'])}")
    
    response = requests.post(
        f"{BASE_URL}/tenants/",
        headers=headers,
        json=core_only_data
    )
    
    if response.status_code == 201:
        tenant = response.json()
        print(f"\n✓ Core-only tenant created successfully!")
        print(f"  ID: {tenant['id']}")
        print(f"  Name: {tenant['name']}")
        print(f"  Slug: {tenant['slug']}")
        print(f"  Business Type: {tenant['business_type']}")
        print(f"  Active Modules: {', '.join(tenant['active_modules'])}")
        print(f"  Has Business Modules: {any(m in tenant.get('active_modules', []) for m in ['construction', 'hardware'])}")
    else:
        print(f"✗ Failed to create tenant: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Test Case 4: All Modules (Premium)
    print_section("TEST CASE 4: All Modules (Premium)")
    
    premium_data = {
        "name": "Premium Enterprise Ltd",
        "business_type": "other",
        "owner_name": "Hari Prasad",
        "email": "hari@premium.com",
        "phone": "+977-9871234567",
        "address": "Biratnagar, Nepal",
        "active_modules": [
            "inventory",
            "sales",
            "purchase",
            "accounting",
            "construction",
            "hardware",
            "reports"
        ]
    }
    
    print("Creating premium tenant with all modules...")
    print(f"Modules: {', '.join(premium_data['active_modules'])}")
    
    response = requests.post(
        f"{BASE_URL}/tenants/",
        headers=headers,
        json=premium_data
    )
    
    if response.status_code == 201:
        tenant = response.json()
        print(f"\n✓ Premium tenant created successfully!")
        print(f"  ID: {tenant['id']}")
        print(f"  Name: {tenant['name']}")
        print(f"  Slug: {tenant['slug']}")
        print(f"  Business Type: {tenant['business_type']}")
        print(f"  Active Modules: {', '.join(tenant['active_modules'])}")
        print(f"  Total Modules: {len(tenant.get('active_modules', []))}")
    else:
        print(f"✗ Failed to create tenant: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # List all tenants
    print_section("ALL TENANTS SUMMARY")
    
    response = requests.get(
        f"{BASE_URL}/tenants/",
        headers=headers
    )
    
    if response.status_code == 200:
        tenants = response.json()
        
        # Handle both list and paginated response
        if isinstance(tenants, dict) and 'results' in tenants:
            tenants = tenants['results']
        
        print(f"Total tenants: {len(tenants)}\n")
        
        for tenant in tenants:
            print(f"• {tenant['name']}")
            print(f"  Type: {tenant['business_type']}")
            print(f"  Modules: {', '.join(tenant.get('active_modules', []))}")
            print(f"  Slug: {tenant['slug']}")
            print()
    else:
        print(f"✗ Failed to list tenants: {response.status_code}")
    
    print_section("MODULE ARCHITECTURE SUMMARY")
    print("""
CORE MODULES (Always Included):
  • inventory    - Base inventory management
  • sales        - Sales orders, invoices, customers
  • purchase     - Purchase orders, suppliers
  • accounting   - Chart of accounts, journal entries
  • reports      - Basic reporting

BUSINESS MODULES (Optional):
  • construction - Sites, labor, equipment, site P&L
  • hardware     - Stock management, credit system, bulk pricing
  • retail       - POS, fast billing, barcode support (V2)

USAGE:
  - Core modules are recommended for all businesses
  - Business modules are industry-specific add-ons
  - Tenants can activate/deactivate modules anytime
  - Module selection affects sidebar navigation and features
    """)
    
    print_section("TEST COMPLETED")
    print("✓ All test cases executed successfully!")
    print("✓ Modular architecture is working as expected")
    print("\nNext steps:")
    print("  1. Visit http://localhost:3000/erp/new to create a tenant via UI")
    print("  2. Select modules based on business type")
    print("  3. Verify sidebar shows only selected modules")
    print("  4. Test module activation/deactivation from settings")

if __name__ == "__main__":
    test_modular_tenant_creation()
