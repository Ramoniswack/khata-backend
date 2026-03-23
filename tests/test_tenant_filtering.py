#!/usr/bin/env python
"""Test tenant filtering in API"""
import requests

API_URL = "http://127.0.0.1:8000/api"

# Login
r = requests.post(f"{API_URL}/auth/login/", json={"username": "efvg", "password": "test123"})
token = r.json()['access']
headers = {"Authorization": f"Bearer {token}"}

# Get categories
cats_response = requests.get(f"{API_URL}/inventory/categories/", headers=headers)
cats = cats_response.json()

if 'results' in cats:
    cats_list = cats['results']
else:
    cats_list = cats

print(f"Categories returned: {len(cats_list)}")
if cats_list:
    print(f"First category: ID={cats_list[0]['id']}, Name={cats_list[0]['name']}")
    print(f"All IDs: {[c['id'] for c in cats_list]}")
