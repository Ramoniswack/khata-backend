#!/usr/bin/env python
"""
Final cleanup - Delete remaining problematic organizations
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from django.db import connection

User = get_user_model()

def final_cleanup():
    print("=" * 70)
    print("FINAL CLEANUP - Delete remaining organizations")
    print("=" * 70)
    
    # Get remaining tenants (except demo)
    tenants = Tenant.objects.exclude(slug='demo-company')
    
    if tenants.count() == 0:
        print("\n✅ No organizations to delete!")
        return
    
    print(f"\nFound {tenants.count()} organizations:")
    for t in tenants:
        print(f"  - {t.name} (slug: {t.slug})")
    
    print("\n🗑️  Deleting all related data using raw SQL...")
    
    with connection.cursor() as cursor:
        for tenant in tenants:
            print(f"\n  Processing: {tenant.name}")
            tenant_id = tenant.id
            
            try:
                # Delete from all tables that reference tenant
                tables = [
                    'sales_invoices',
                    'sales_quotations',
                    'sales_salesorders',
                    'sales_creditnotes',
                    'sales_paymentsreceived',
                    'sales_customers',
                    'purchase_purchaseinvoices',
                    'purchase_purchaseorders',
                    'purchase_debitnotes',
                    'purchase_suppliers',
                    'inventory_products',
                    'inventory_categories',
                    'inventory_warehouses',
                    'inventory_stockmovements',
                    'inventory_unitofmeasures',
                    'accounting_accounts',
                    'accounting_journalentries',
                    'accounting_taxrules',
                    'accounting_bankaccounts',
                    'hr_employees',
                    'hr_departments',
                    'hr_attendance',
                    'hr_leaverequests',
                    'hr_payroll',
                    'construction_sites',
                    'construction_materialconsumptions',
                    'reports_customreport',
                ]
                
                for table in tables:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE tenant_id = %s", [tenant_id])
                        deleted = cursor.rowcount
                        if deleted > 0:
                            print(f"    ✓ Deleted {deleted} rows from {table}")
                    except Exception as e:
                        if "no such table" not in str(e).lower():
                            print(f"    ⚠️  {table}: {str(e)[:50]}")
                
                # Finally delete the tenant
                cursor.execute("DELETE FROM tenants WHERE id = %s", [tenant_id])
                print(f"    ✅ Deleted organization")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("FINAL CLEANUP COMPLETE")
    print(f"{'='*70}")
    
    remaining = Tenant.objects.count()
    print(f"\nRemaining organizations: {remaining}")
    
    for t in Tenant.objects.all():
        users = User.objects.filter(tenant=t).count()
        print(f"  - {t.name} ({users} users)")
    
    print(f"\n✅ Database is clean!")

if __name__ == "__main__":
    final_cleanup()
