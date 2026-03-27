#!/usr/bin/env python
"""
Force delete all test organizations and users (NO CONFIRMATION)
WARNING: This will delete ALL data except the demo company and admin user
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from hr.models import Employee, Department

User = get_user_model()

def force_cleanup():
    print("=" * 70)
    print("⚠️  FORCE DELETING ALL TEST DATA (NO CONFIRMATION)")
    print("=" * 70)
    
    # Protected items (won't delete)
    protected_emails = ['admin@khata.com']
    protected_tenants = ['demo-company']
    
    print("\nProtected items (will NOT be deleted):")
    print(f"  - Users: {', '.join(protected_emails)}")
    print(f"  - Organizations: {', '.join(protected_tenants)}")
    
    # Get all tenants except protected ones
    tenants_to_delete = Tenant.objects.exclude(slug__in=protected_tenants)
    tenant_count = tenants_to_delete.count()
    
    print(f"\n📊 Current Database State:")
    print(f"  - Total Organizations: {Tenant.objects.count()}")
    print(f"  - Organizations to delete: {tenant_count}")
    print(f"  - Total Users: {User.objects.count()}")
    print(f"  - Users to delete: {User.objects.exclude(email__in=protected_emails).count()}")
    
    if tenant_count == 0:
        print("\n✅ No organizations to delete!")
        return
    
    print(f"\n🗑️  Starting deletion process...")
    
    # Delete tenants (this will cascade delete most related data)
    deleted_count = 0
    errors = []
    
    for tenant in tenants_to_delete:
        try:
            # Delete HR data first (protected foreign keys)
            emp_count = Employee.objects.filter(tenant=tenant).count()
            dept_count = Department.objects.filter(tenant=tenant).count()
            
            if emp_count > 0 or dept_count > 0:
                Employee.objects.filter(tenant=tenant).delete()
                Department.objects.filter(tenant=tenant).delete()
            
            # Unassign users
            user_count = User.objects.filter(tenant=tenant).count()
            if user_count > 0:
                User.objects.filter(tenant=tenant).update(tenant=None)
            
            # Delete tenant
            tenant_name = tenant.name
            tenant.delete()
            deleted_count += 1
            
            if deleted_count % 10 == 0:
                print(f"  ✓ Deleted {deleted_count}/{tenant_count} organizations...")
            
        except Exception as e:
            errors.append(f"{tenant.name}: {str(e)}")
            print(f"  ❌ Error deleting {tenant.name}: {e}")
    
    print(f"\n✅ Deleted {deleted_count} organizations")
    
    # Delete users without tenants (except protected)
    orphan_users = User.objects.filter(tenant__isnull=True).exclude(email__in=protected_emails)
    orphan_count = orphan_users.count()
    
    if orphan_count > 0:
        print(f"\n🗑️  Deleting {orphan_count} users without organizations...")
        orphan_users.delete()
        print(f"✅ Deleted {orphan_count} orphan users")
    
    # Show errors if any
    if errors:
        print(f"\n⚠️  Errors encountered ({len(errors)}):")
        for error in errors[:10]:
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    # Final summary
    print(f"\n{'='*70}")
    print("CLEANUP COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Final Database State:")
    print(f"  - Organizations: {Tenant.objects.count()}")
    print(f"  - Users: {User.objects.count()}")
    
    remaining_tenants = Tenant.objects.all()
    if remaining_tenants.exists():
        print(f"\n📋 Remaining Organizations:")
        for tenant in remaining_tenants:
            user_count = User.objects.filter(tenant=tenant).count()
            print(f"  - {tenant.name} (slug: {tenant.slug}) - {user_count} users")
    
    remaining_users = User.objects.all()
    if remaining_users.exists():
        print(f"\n👥 Remaining Users:")
        for user in remaining_users:
            tenant_name = user.tenant.name if user.tenant else "No organization"
            print(f"  - {user.email} (role: {user.role}) - {tenant_name}")
    
    print(f"\n✅ Database cleaned successfully!")
    print(f"   Deleted: {deleted_count} organizations, {orphan_count} users")
    if errors:
        print(f"   Errors: {len(errors)}")

if __name__ == "__main__":
    force_cleanup()
