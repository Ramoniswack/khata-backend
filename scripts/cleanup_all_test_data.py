#!/usr/bin/env python
"""
Delete all test organizations and users
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

def cleanup_all():
    print("=" * 70)
    print("⚠️  WARNING: DELETING ALL TEST DATA")
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
    
    print(f"\n📋 Organizations that will be deleted:")
    for tenant in tenants_to_delete[:20]:  # Show first 20
        user_count = User.objects.filter(tenant=tenant).count()
        print(f"  - {tenant.name} (slug: {tenant.slug}) - {user_count} users")
    
    if tenant_count > 20:
        print(f"  ... and {tenant_count - 20} more")
    
    # Ask for confirmation
    print(f"\n{'='*70}")
    print("⚠️  THIS WILL DELETE:")
    print(f"  - {tenant_count} organizations")
    print(f"  - All associated data (products, invoices, employees, etc.)")
    print(f"  - {User.objects.exclude(email__in=protected_emails).count()} users")
    print(f"{'='*70}")
    
    response = input("\nType 'DELETE ALL' to confirm (or anything else to cancel): ")
    
    if response != 'DELETE ALL':
        print("\n❌ Cancelled. No data was deleted.")
        return
    
    print("\n🗑️  Starting deletion process...")
    
    # Delete tenants (this will cascade delete most related data)
    deleted_count = 0
    for tenant in tenants_to_delete:
        try:
            # Delete HR data first (protected foreign keys)
            emp_count = Employee.objects.filter(tenant=tenant).count()
            dept_count = Department.objects.filter(tenant=tenant).count()
            
            if emp_count > 0 or dept_count > 0:
                Employee.objects.filter(tenant=tenant).delete()
                Department.objects.filter(tenant=tenant).delete()
                print(f"  ✓ Deleted {emp_count} employees, {dept_count} departments from {tenant.name}")
            
            # Unassign users
            user_count = User.objects.filter(tenant=tenant).count()
            if user_count > 0:
                User.objects.filter(tenant=tenant).update(tenant=None)
                print(f"  ✓ Unassigned {user_count} users from {tenant.name}")
            
            # Delete tenant
            tenant_name = tenant.name
            tenant.delete()
            deleted_count += 1
            print(f"  ✅ Deleted organization: {tenant_name}")
            
        except Exception as e:
            print(f"  ❌ Error deleting {tenant.name}: {e}")
    
    print(f"\n✅ Deleted {deleted_count} organizations")
    
    # Delete users without tenants (except protected)
    orphan_users = User.objects.filter(tenant__isnull=True).exclude(email__in=protected_emails)
    orphan_count = orphan_users.count()
    
    if orphan_count > 0:
        print(f"\n🗑️  Deleting {orphan_count} users without organizations...")
        orphan_users.delete()
        print(f"✅ Deleted {orphan_count} orphan users")
    
    # Final summary
    print(f"\n{'='*70}")
    print("CLEANUP COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Remaining Database State:")
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

if __name__ == "__main__":
    cleanup_all()
