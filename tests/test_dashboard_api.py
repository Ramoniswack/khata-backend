"""
Test script for dashboard API endpoints
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from reports.views import ReportViewSet
from datetime import datetime, timedelta

User = get_user_model()

def test_dashboard_endpoints():
    """Test dashboard-summary and profit-and-loss endpoints"""
    
    # Get a test user with tenant
    user = User.objects.filter(tenant__isnull=False).first()
    
    if not user:
        print("❌ No user with tenant found. Please create a user with tenant first.")
        return
    
    print(f"✅ Testing with user: {user.email} (Tenant: {user.tenant.name})")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Dashboard Summary
    print("\n" + "="*60)
    print("TEST 1: Dashboard Summary")
    print("="*60)
    
    request = factory.get('/api/reports/dashboard-summary/')
    force_authenticate(request, user=user)
    
    view = ReportViewSet.as_view({'get': 'dashboard_summary'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print("✅ Dashboard Summary Response:")
        print(f"  Financials:")
        print(f"    - Total Receivables: {data['financials']['total_receivables']}")
        print(f"    - Total Payables: {data['financials']['total_payables']}")
        print(f"    - Total Revenue: {data['financials']['total_revenue']}")
        print(f"    - Total Expenses: {data['financials']['total_expenses']}")
        print(f"    - Net Profit: {data['financials']['net_profit']}")
        print(f"    - Profit Margin: {data['financials']['profit_margin_percentage']}%")
        print(f"  Inventory:")
        print(f"    - Low Stock Items: {data['inventory']['total_low_stock_items']}")
        print(f"    - Critical Items: {data['inventory']['critical_items']}")
        print(f"  Construction:")
        print(f"    - Budget Alert Sites: {data['construction']['total_alert_sites']}")
        print(f"    - Critical Sites: {data['construction']['critical_sites']}")
        print(f"    - Total Active Sites: {data['construction']['total_active_sites']}")
    else:
        print(f"❌ Error: {response.data}")
    
    # Test 2: Profit and Loss
    print("\n" + "="*60)
    print("TEST 2: Profit and Loss")
    print("="*60)
    
    # Date range: last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    request = factory.get(
        f'/api/reports/profit-and-loss/?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
    )
    force_authenticate(request, user=user)
    
    view = ReportViewSet.as_view({'get': 'profit_and_loss'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Date Range: {start_date} to {end_date}")
    
    if response.status_code == 200:
        data = response.data
        print("✅ Profit & Loss Response:")
        print(f"  Period: {data['period']['days']} days")
        print(f"  Revenue:")
        print(f"    - Sales Revenue: {data['revenue']['sales_revenue']['amount']} ({data['revenue']['sales_revenue']['count']} orders)")
        print(f"    - Invoice Revenue: {data['revenue']['invoice_revenue']['amount']} ({data['revenue']['invoice_revenue']['count']} invoices)")
        print(f"    - Total Revenue: {data['revenue']['total_revenue']}")
        print(f"  Expenses:")
        print(f"    - Purchase Expenses: {data['expenses']['purchase_expenses']['amount']}")
        print(f"    - Material Expenses: {data['expenses']['material_expenses']['amount']}")
        print(f"    - Labor Expenses: {data['expenses']['labor_expenses']['amount']}")
        print(f"    - Total Expenses: {data['expenses']['total_expenses']}")
        print(f"  Profit:")
        print(f"    - Gross Profit: {data['profit']['gross_profit']}")
        print(f"    - Gross Profit Margin: {data['profit']['gross_profit_margin_percentage']}%")
        print(f"    - Net Profit: {data['profit']['net_profit']}")
        print(f"    - Net Profit Margin: {data['profit']['net_profit_margin_percentage']}%")
        print(f"  Metrics:")
        print(f"    - Avg Daily Revenue: {data['metrics']['average_daily_revenue']}")
        print(f"    - Avg Daily Expenses: {data['metrics']['average_daily_expenses']}")
        print(f"    - Expense Ratio: {data['metrics']['expense_ratio_percentage']}%")
    else:
        print(f"❌ Error: {response.data}")
    
    # Test 3: Without date range (should fail)
    print("\n" + "="*60)
    print("TEST 3: Profit and Loss (No Date Range - Should Fail)")
    print("="*60)
    
    request = factory.get('/api/reports/profit-and-loss/')
    force_authenticate(request, user=user)
    
    view = ReportViewSet.as_view({'get': 'profit_and_loss'})
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected: {response.data}")
    else:
        print(f"❌ Unexpected response: {response.data}")
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_dashboard_endpoints()
