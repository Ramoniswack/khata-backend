#!/usr/bin/env python
"""
Nuclear cleanup - Delete EVERYTHING except demo company
Handles all protected foreign keys
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from hr.models import Employee, Department, Attendance, LeaveRequest, Payroll
from construction.models import Site, MaterialConsumption
from sales.models import Customer, Invoice, Quotation, SalesOrder, CreditNote, PaymentReceived
from purchase.models import Supplier, PurchaseOrder, PurchaseInvoice, DebitNote
from inventory.models import Product, Category, Warehouse, StockMovement, UnitOfMeasure
from accounting.models import Account, JournalEntry, JournalLine, TaxRule, BankAccount

User = get_user_model()

def nuclear_cleanup():
    print("=" * 70)
    print("☢️  NUCLEAR CLEANUP - DELETING EVERYTHING")
    print("=" * 70)
    
    # Protected items
    protected_emails = ['admin@khata.com']
    protected_tenants = ['demo-company']
    
    print("\nProtected (will NOT delete):")
    print(f"  - Users: {', '.join(protected_emails)}")
    print(f"  - Organizations: {', '.join(protected_tenants)}")
    
    # Get tenants to delete
    tenants_to_delete = Tenant.objects.exclude(slug__in=protected_tenants)
    tenant_count = tenants_to_delete.count()
    
    print(f"\n📊 Will delete {tenant_count} organizations and ALL their data")
    
    if tenant_count == 0:
        print("\n✅ Nothing to delete!")
        return
    
    print(f"\n🗑️  Starting nuclear cleanup...")
    
    deleted_stats = {
        'tenants': 0,
        'users': 0,
        'employees': 0,
        'departments': 0,
        'sites': 0,
        'customers': 0,
        'suppliers': 0,
        'products': 0,
        'invoices': 0,
        'orders': 0,
        'accounts': 0,
    }
    
    for tenant in tenants_to_delete:
        try:
            print(f"\n  🗑️  Deleting: {tenant.name}")
            
            # Delete in correct order to handle foreign keys
            
            # 1. Delete journal entries (has posted_by foreign key to User)
            journal_entries = JournalEntry.objects.filter(tenant=tenant)
            je_count = journal_entries.count()
            if je_count > 0:
                # Delete journal lines first
                JournalLine.objects.filter(journal_entry__tenant=tenant).delete()
                journal_entries.delete()
                print(f"     ✓ Deleted {je_count} journal entries")
            
            # 2. Delete sales data (invoices reference customers)
            invoices = Invoice.objects.filter(tenant=tenant)
            inv_count = invoices.count()
            if inv_count > 0:
                invoices.delete()
                deleted_stats['invoices'] += inv_count
            
            PaymentReceived.objects.filter(tenant=tenant).delete()
            CreditNote.objects.filter(tenant=tenant).delete()
            SalesOrder.objects.filter(tenant=tenant).delete()
            Quotation.objects.filter(tenant=tenant).delete()
            
            customers = Customer.objects.filter(tenant=tenant)
            cust_count = customers.count()
            if cust_count > 0:
                customers.delete()
                deleted_stats['customers'] += cust_count
            
            # 3. Delete purchase data (purchase invoices reference suppliers)
            PurchaseInvoice.objects.filter(tenant=tenant).delete()
            DebitNote.objects.filter(tenant=tenant).delete()
            PurchaseOrder.objects.filter(tenant=tenant).delete()
            
            suppliers = Supplier.objects.filter(tenant=tenant)
            supp_count = suppliers.count()
            if supp_count > 0:
                suppliers.delete()
                deleted_stats['suppliers'] += supp_count
            
            # 4. Delete construction sites (has manager foreign key to User)
            sites = Site.objects.filter(tenant=tenant)
            site_count = sites.count()
            if site_count > 0:
                # Delete material consumption first
                MaterialConsumption.objects.filter(site__tenant=tenant).delete()
                # Unassign managers (set to null)
                sites.update(manager=None)
                sites.delete()
                deleted_stats['sites'] += site_count
                print(f"     ✓ Deleted {site_count} sites")
            
            # 5. Delete inventory data
            StockMovement.objects.filter(tenant=tenant).delete()
            products = Product.objects.filter(tenant=tenant)
            prod_count = products.count()
            if prod_count > 0:
                products.delete()
                deleted_stats['products'] += prod_count
            
            Category.objects.filter(tenant=tenant).delete()
            Warehouse.objects.filter(tenant=tenant).delete()
            UnitOfMeasure.objects.filter(tenant=tenant).delete()
            
            # 6. Delete accounting data
            BankAccount.objects.filter(tenant=tenant).delete()
            TaxRule.objects.filter(tenant=tenant).delete()
            accounts = Account.objects.filter(tenant=tenant)
            acc_count = accounts.count()
            if acc_count > 0:
                accounts.delete()
                deleted_stats['accounts'] += acc_count
            
            # 7. Delete HR data
            Payroll.objects.filter(tenant=tenant).delete()
            LeaveRequest.objects.filter(tenant=tenant).delete()
            Attendance.objects.filter(tenant=tenant).delete()
            
            employees = Employee.objects.filter(tenant=tenant)
            emp_count = employees.count()
            if emp_count > 0:
                employees.delete()
                deleted_stats['employees'] += emp_count
            
            departments = Department.objects.filter(tenant=tenant)
            dept_count = departments.count()
            if dept_count > 0:
                departments.delete()
                deleted_stats['departments'] += dept_count
            
            # 8. Unassign users
            users = User.objects.filter(tenant=tenant)
            user_count = users.count()
            if user_count > 0:
                users.update(tenant=None)
            
            # 9. Finally delete tenant
            tenant.delete()
            deleted_stats['tenants'] += 1
            print(f"     ✅ Deleted organization")
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Delete orphan users (except protected)
    # First, unassign them from any remaining sites
    orphan_users = User.objects.filter(tenant__isnull=True).exclude(email__in=protected_emails)
    orphan_count = orphan_users.count()
    
    if orphan_count > 0:
        print(f"\n🗑️  Deleting {orphan_count} orphan users...")
        # Unassign from any sites first
        Site.objects.filter(manager__in=orphan_users).update(manager=None)
        orphan_users.delete()
        deleted_stats['users'] = orphan_count
    
    # Final summary
    print(f"\n{'='*70}")
    print("NUCLEAR CLEANUP COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Deleted:")
    print(f"  - Organizations: {deleted_stats['tenants']}")
    print(f"  - Users: {deleted_stats['users']}")
    print(f"  - Employees: {deleted_stats['employees']}")
    print(f"  - Departments: {deleted_stats['departments']}")
    print(f"  - Sites: {deleted_stats['sites']}")
    print(f"  - Customers: {deleted_stats['customers']}")
    print(f"  - Suppliers: {deleted_stats['suppliers']}")
    print(f"  - Products: {deleted_stats['products']}")
    print(f"  - Invoices: {deleted_stats['invoices']}")
    print(f"  - Accounts: {deleted_stats['accounts']}")
    
    print(f"\n📊 Remaining:")
    print(f"  - Organizations: {Tenant.objects.count()}")
    print(f"  - Users: {User.objects.count()}")
    
    remaining_tenants = Tenant.objects.all()
    if remaining_tenants.exists():
        print(f"\n📋 Remaining Organizations:")
        for tenant in remaining_tenants:
            user_count = User.objects.filter(tenant=tenant).count()
            print(f"  - {tenant.name} ({user_count} users)")
    
    remaining_users = User.objects.all()
    if remaining_users.exists():
        print(f"\n👥 Remaining Users:")
        for user in remaining_users:
            tenant_name = user.tenant.name if user.tenant else "No org"
            print(f"  - {user.email} ({user.role}) - {tenant_name}")
    
    print(f"\n✅ Database is now clean!")

if __name__ == "__main__":
    nuclear_cleanup()
