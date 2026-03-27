#!/usr/bin/env python
"""Activate reports module for Demo Company tenant"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from users.models import User

def activate_module():
    """Activate reports module"""
    print("🔧 Activating reports module...")
    
    # Get admin user's tenant
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found")
        return
    
    tenant = admin.tenant
    if not tenant:
        print("❌ Admin has no tenant")
        return
    
    print(f"✅ Found tenant: {tenant.name}")
    print(f"   Current modules: {tenant.active_modules}")
    
    # Add reports module if not present
    if 'reports' not in tenant.active_modules:
        tenant.active_modules.append('reports')
        tenant.save()
        print(f"   ✅ Added 'reports' module")
    else:
        print(f"   ℹ️  'reports' module already active")
    
    print(f"   Final modules: {tenant.active_modules}")

if __name__ == "__main__":
    activate_module()
