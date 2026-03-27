#!/usr/bin/env python
"""
Simple cleanup - Just delete all sites and tenants, keep users
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from construction.models import Site

User = get_user_model()

def simple_cleanup():
    print("=" * 70)
    print("SIMPLE CLEANUP - Delete all organizations and sites")
    print("=" * 70)
    
    # Protected
    protected_tenants = ['demo-company']
    
    # Step 1: Delete ALL sites (they block user deletion)
    print("\n1. Deleting ALL construction sites...")
    sites = Site.objects.all()
    site_count = sites.count()
    if site_count > 0:
        sites.delete()
        print(f"   ✅ Deleted {site_count} sites")
    else:
        print(f"   ℹ️  No sites to delete")
    
    # Step 2: Delete all tenants except protected
    print("\n2. Deleting organizations...")
    tenants = Tenant.objects.exclude(slug__in=protected_tenants)
    tenant_count = tenants.count()
    
    if tenant_count == 0:
        print(f"   ℹ️  No organizations to delete")
        return
    
    print(f"   Found {tenant_count} organizations to delete")
    
    deleted = 0
    errors = []
    
    for tenant in tenants:
        try:
            # Unassign users
            User.objects.filter(tenant=tenant).update(tenant=None)
            
            # Delete tenant
            tenant.delete()
            deleted += 1
            
            if deleted % 10 == 0:
                print(f"   ✓ Deleted {deleted}/{tenant_count}...")
                
        except Exception as e:
            errors.append(f"{tenant.name}: {str(e)[:100]}")
    
    print(f"   ✅ Deleted {deleted} organizations")
    
    if errors:
        print(f"\n   ⚠️  {len(errors)} errors:")
        for err in errors[:5]:
            print(f"      - {err}")
    
    # Step 3: Delete orphan users
    print("\n3. Deleting users without organizations...")
    orphans = User.objects.filter(tenant__isnull=True).exclude(email='admin@khata.com')
    orphan_count = orphans.count()
    
    if orphan_count > 0:
        orphans.delete()
        print(f"   ✅ Deleted {orphan_count} users")
    else:
        print(f"   ℹ️  No orphan users")
    
    # Summary
    print(f"\n{'='*70}")
    print("CLEANUP COMPLETE")
    print(f"{'='*70}")
    print(f"\nRemaining:")
    print(f"  - Organizations: {Tenant.objects.count()}")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Sites: {Site.objects.count()}")
    
    remaining_tenants = Tenant.objects.all()
    if remaining_tenants.exists():
        print(f"\nOrganizations:")
        for t in remaining_tenants:
            users = User.objects.filter(tenant=t).count()
            print(f"  - {t.name} ({users} users)")
    
    remaining_users = User.objects.all()
    if remaining_users.exists():
        print(f"\nUsers:")
        for u in remaining_users:
            org = u.tenant.name if u.tenant else "No org"
            print(f"  - {u.email} ({u.role}) - {org}")

if __name__ == "__main__":
    simple_cleanup()
