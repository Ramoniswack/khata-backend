#!/usr/bin/env python
"""
Test script to create a product via API and see the actual error
"""
import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000/api"
USERNAME = "efvg"  # Replace with your username
PASSWORD = "test123"  # Replace with your password

def main():
    # Step 1: Login to get token
    print("Step 1: Logging in...")
    login_response = requests.post(
        f"{API_URL}/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    tokens = login_response.json()
    access_token = tokens['access']
    print(f"✓ Login successful")
    
    # Step 2: Get categories
    print("\nStep 2: Fetching categories...")
    headers = {"Authorization": f"Bearer {access_token}"}
    categories_response = requests.get(f"{API_URL}/inventory/categories/", headers=headers)
    
    if categories_response.status_code != 200:
        print(f"Failed to fetch categories: {categories_response.status_code}")
        print(categories_response.text)
        return
    
    categories = categories_response.json()
    # Handle paginated response
    if isinstance(categories, dict) and 'results' in categories:
        categories = categories['results']
    
    if not categories:
        print("No categories found!")
        return
    
    category_id = categories[0]['id']
    print(f"✓ Found {len(categories)} categories, using: {categories[0]['name']} (ID: {category_id})")
    
    # Step 3: Get units
    print("\nStep 3: Fetching units...")
    units_response = requests.get(f"{API_URL}/inventory/units/", headers=headers)
    
    if units_response.status_code != 200:
        print(f"Failed to fetch units: {units_response.status_code}")
        print(units_response.text)
        return
    
    units = units_response.json()
    # Handle paginated response
    if isinstance(units, dict) and 'results' in units:
        units = units['results']
    
    if not units:
        print("No units found!")
        return
    
    unit_id = units[0]['id']
    print(f"✓ Found {len(units)} units, using: {units[0]['name']} (ID: {unit_id})")
    
    # Step 4: Create product
    print("\nStep 4: Creating product...")
    product_data = {
        "name": "Test Product API",
        "sku": "TEST-API-001",
        "category": category_id,
        "unit": unit_id,
        "cost_price": 100.00,
        "selling_price": 150.00,
        "reorder_level": 10,
        "description": "Test product created via API",
        "status": "active"
    }
    
    print(f"Payload: {json.dumps(product_data, indent=2)}")
    
    create_response = requests.post(
        f"{API_URL}/inventory/products/",
        headers=headers,
        json=product_data
    )
    
    print(f"\nResponse Status: {create_response.status_code}")
    print(f"Response Headers: {dict(create_response.headers)}")
    print(f"\nResponse Body:")
    
    try:
        response_json = create_response.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(create_response.text[:1000])  # Print first 1000 chars if not JSON
    
    if create_response.status_code == 201:
        print("\n✓ Product created successfully!")
    else:
        print(f"\n✗ Product creation failed with status {create_response.status_code}")
        
        # Try the test endpoint
        print("\n\nStep 5: Trying test endpoint...")
        test_response = requests.post(
            f"{API_URL}/inventory/test-create-product/",
            headers=headers,
            json=product_data
        )
        
        print(f"Test Response Status: {test_response.status_code}")
        try:
            test_json = test_response.json()
            print(json.dumps(test_json, indent=2))
        except:
            print(test_response.text[:1000])

if __name__ == "__main__":
    main()
