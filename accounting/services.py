"""
Accounting Services - Core Layer
Provides accounting operations used by all industry modules.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from accounting.models import JournalEntry, JournalLine, Account
from tenants.middleware import get_current_tenant


def create_journal_entry(tenant, description, entries, reference=None, date=None):
    """
    Create a double-entry journal entry.
    
    This is the CORE accounting function used by all modules to record
    financial transactions. Ensures double-entry bookkeeping is maintained.
    
    Args:
        tenant: Tenant instance
        description: Entry description
        entries: List of dicts with 'account', 'debit', 'credit'
                 Example: [
                     {'account': account_obj, 'debit': 1000, 'credit': 0},
                     {'account': account_obj, 'debit': 0, 'credit': 1000}
                 ]
        reference: Optional reference number (e.g., invoice number)
        date: Optional date (defaults to today)
    
    Returns:
        JournalEntry instance
    
    Raises:
        ValueError: If debits don't equal credits
    """
    with transaction.atomic():
        # Validate double-entry
        total_debit = sum(Decimal(str(e['debit'])) for e in entries)
        total_credit = sum(Decimal(str(e['credit'])) for e in entries)
        
        if total_debit != total_credit:
            raise ValueError(
                f"Debits ({total_debit}) must equal credits ({total_credit}). "
                f"Double-entry bookkeeping violation."
            )
        
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            tenant=tenant,
            date=date or timezone.now().date(),
            description=description,
            reference=reference or '',
            total_amount=total_debit
        )
        
        # Create journal lines
        for entry in entries:
            JournalLine.objects.create(
                tenant=tenant,
                journal_entry=journal_entry,
                account=entry['account'],
                debit=Decimal(str(entry['debit'])),
                credit=Decimal(str(entry['credit'])),
                description=entry.get('description', description)
            )
        
        return journal_entry


# ============================================================================
# CORE ACCOUNT GETTERS
# These functions ensure standard accounts exist for all tenants
# ============================================================================

def get_or_create_account(code, name, account_type):
    """Helper to get or create a standard account"""
    tenant = get_current_tenant()
    if not tenant:
        raise ValueError("No tenant in context. Cannot create account.")
    
    account, created = Account.objects.get_or_create(
        tenant=tenant,
        code=code,
        defaults={
            'name': name,
            'account_type': account_type,
            'is_active': True
        }
    )
    return account


def get_cash_account():
    """Get or create Cash account (Asset)"""
    return get_or_create_account('1000', 'Cash', 'asset')


def get_accounts_receivable_account():
    """Get or create Accounts Receivable account (Asset)"""
    return get_or_create_account('1100', 'Accounts Receivable', 'asset')


def get_inventory_asset_account():
    """Get or create Inventory account (Asset)"""
    return get_or_create_account('1200', 'Inventory', 'asset')


def get_accounts_payable_account():
    """Get or create Accounts Payable account (Liability)"""
    return get_or_create_account('2000', 'Accounts Payable', 'liability')


def get_wages_payable_account():
    """Get or create Wages Payable account (Liability)"""
    return get_or_create_account('2100', 'Wages Payable', 'liability')


def get_sales_revenue_account():
    """Get or create Sales Revenue account (Revenue)"""
    return get_or_create_account('4000', 'Sales Revenue', 'revenue')


def get_cost_of_goods_sold_account():
    """Get or create Cost of Goods Sold account (Expense)"""
    return get_or_create_account('5000', 'Cost of Goods Sold', 'expense')


def get_construction_expense_account():
    """Get or create Construction Expense account (Expense)"""
    return get_or_create_account('5100', 'Construction Expenses', 'expense')


def get_labor_expense_account():
    """Get or create Labor Expense account (Expense)"""
    return get_or_create_account('5200', 'Labor Expenses', 'expense')


def get_equipment_expense_account():
    """Get or create Equipment Expense account (Expense)"""
    return get_or_create_account('5300', 'Equipment Expenses', 'expense')


# ============================================================================
# INDUSTRY MODULE HELPERS
# These functions are called by industry modules to record transactions
# ============================================================================

def record_material_consumption(site, product, quantity, unit_cost, reference):
    """
    Record material consumption for construction site.
    Called by Construction module.
    
    Accounting Entry:
    Dr. Construction Expense (Site Cost Center)
    Cr. Inventory Asset
    """
    tenant = get_current_tenant()
    total_cost = Decimal(str(quantity)) * Decimal(str(unit_cost))
    
    # Get site's cost center account or use default construction expense
    cost_center = getattr(site, 'cost_center_account', None) or get_construction_expense_account()
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Material consumption: {product.name} at {site.name}",
        reference=reference,
        entries=[
            {
                'account': cost_center,
                'debit': total_cost,
                'credit': 0,
                'description': f"Material: {product.name} ({quantity} units)"
            },
            {
                'account': get_inventory_asset_account(),
                'debit': 0,
                'credit': total_cost,
                'description': f"Stock reduction: {product.name}"
            }
        ]
    )


def record_labor_wage(site, worker, wage_amount, date, reference):
    """
    Record labor wage expense for construction site.
    Called by Construction module.
    
    Accounting Entry:
    Dr. Labor Expense (Site Cost Center)
    Cr. Wages Payable
    """
    tenant = get_current_tenant()
    wage_amount = Decimal(str(wage_amount))
    
    # Get site's cost center account or use default labor expense
    cost_center = getattr(site, 'cost_center_account', None) or get_labor_expense_account()
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Labor wage: {worker.name} at {site.name}",
        reference=reference,
        date=date,
        entries=[
            {
                'account': cost_center,
                'debit': wage_amount,
                'credit': 0,
                'description': f"Worker: {worker.name} ({worker.category})"
            },
            {
                'account': get_wages_payable_account(),
                'debit': 0,
                'credit': wage_amount,
                'description': f"Wage payable to {worker.name}"
            }
        ]
    )


def record_credit_sale(customer, total_amount, reference):
    """
    Record credit sale to customer.
    Called by Sales module (Hardware).
    
    Accounting Entry:
    Dr. Accounts Receivable
    Cr. Sales Revenue
    """
    tenant = get_current_tenant()
    total_amount = Decimal(str(total_amount))
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Credit sale to {customer.name}",
        reference=reference,
        entries=[
            {
                'account': get_accounts_receivable_account(),
                'debit': total_amount,
                'credit': 0,
                'description': f"Customer: {customer.name}"
            },
            {
                'account': get_sales_revenue_account(),
                'debit': 0,
                'credit': total_amount,
                'description': f"Sale to {customer.name}"
            }
        ]
    )


def record_cash_sale(total_amount, reference, customer_name=None):
    """
    Record cash sale.
    Called by Sales module.
    
    Accounting Entry:
    Dr. Cash
    Cr. Sales Revenue
    """
    tenant = get_current_tenant()
    total_amount = Decimal(str(total_amount))
    
    description = f"Cash sale"
    if customer_name:
        description += f" to {customer_name}"
    
    return create_journal_entry(
        tenant=tenant,
        description=description,
        reference=reference,
        entries=[
            {
                'account': get_cash_account(),
                'debit': total_amount,
                'credit': 0,
                'description': description
            },
            {
                'account': get_sales_revenue_account(),
                'debit': 0,
                'credit': total_amount,
                'description': description
            }
        ]
    )


def record_purchase(supplier, total_amount, reference):
    """
    Record purchase from supplier.
    Called by Purchase module.
    
    Accounting Entry:
    Dr. Inventory Asset
    Cr. Accounts Payable
    """
    tenant = get_current_tenant()
    total_amount = Decimal(str(total_amount))
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Purchase from {supplier.name}",
        reference=reference,
        entries=[
            {
                'account': get_inventory_asset_account(),
                'debit': total_amount,
                'credit': 0,
                'description': f"Supplier: {supplier.name}"
            },
            {
                'account': get_accounts_payable_account(),
                'debit': 0,
                'credit': total_amount,
                'description': f"Payable to {supplier.name}"
            }
        ]
    )


def record_payment_to_supplier(supplier, amount, reference):
    """
    Record payment to supplier.
    
    Accounting Entry:
    Dr. Accounts Payable
    Cr. Cash
    """
    tenant = get_current_tenant()
    amount = Decimal(str(amount))
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Payment to {supplier.name}",
        reference=reference,
        entries=[
            {
                'account': get_accounts_payable_account(),
                'debit': amount,
                'credit': 0,
                'description': f"Payment to {supplier.name}"
            },
            {
                'account': get_cash_account(),
                'debit': 0,
                'credit': amount,
                'description': f"Cash paid to {supplier.name}"
            }
        ]
    )


def record_payment_from_customer(customer, amount, reference):
    """
    Record payment received from customer.
    
    Accounting Entry:
    Dr. Cash
    Cr. Accounts Receivable
    """
    tenant = get_current_tenant()
    amount = Decimal(str(amount))
    
    return create_journal_entry(
        tenant=tenant,
        description=f"Payment from {customer.name}",
        reference=reference,
        entries=[
            {
                'account': get_cash_account(),
                'debit': amount,
                'credit': 0,
                'description': f"Payment from {customer.name}"
            },
            {
                'account': get_accounts_receivable_account(),
                'debit': 0,
                'credit': amount,
                'description': f"Receivable from {customer.name}"
            }
        ]
    )
