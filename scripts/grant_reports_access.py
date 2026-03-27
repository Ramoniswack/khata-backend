#!/usr/bin/env python
"""Grant reports module access to admin user"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User

def grant_access():
    """Grant reports access to admin"""
    print("🔑 Granting reports module access...")
    
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found")
        return
    
    print(f"✅ Found admin: {admin.username}")
    
    # Check current modules
    print(f"   Current modules: {admin.modules}")
    
    # Add reports module if not present
    if 'reports' not in admin.modules:
        admin.modules.append('reports')
        admin.save()
        print(f"   ✅ Added 'reports' module")
    else:
        print(f"   ℹ️  'reports' module already present")
    
    print(f"   Final modules: {admin.modules}")

if __name__ == "__main__":
    grant_access()
