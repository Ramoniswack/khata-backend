#!/usr/bin/env python
"""
Test script for construction site report generation
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from construction.models import Site
from django.contrib.auth import get_user_model

User = get_user_model()

def test_site_report():
    """Test site report generation"""
    print("\n" + "="*80)
    print("TESTING CONSTRUCTION SITE REPORT GENERATION")
    print("="*80)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    print(f"\n✓ Using user: {user.email}")
    print(f"✓ Tenant: {user.tenant.name if user.tenant else 'None'}")
    
    # Get sites for this tenant
    sites = Site.objects.filter(tenant=user.tenant)
    print(f"\n✓ Found {sites.count()} sites")
    
    if not sites.exists():
        print("❌ No sites found for this tenant")
        return
    
    # Test report generation for each site
    for site in sites:
        print(f"\n{'='*80}")
        print(f"Testing report for: {site.name}")
        print(f"{'='*80}")
        
        try:
            # Test cost calculations
            material_cost = site.get_material_cost()
            labor_cost = site.get_labor_cost()
            other_expenses = site.get_other_expenses()
            actual_spend = site.get_actual_spend()
            remaining_budget = site.get_remaining_budget()
            budget_percentage = site.get_budget_percentage()
            
            print(f"\n✓ Site: {site.name}")
            print(f"  Location: {site.location}")
            print(f"  Client: {site.client_name or 'N/A'}")
            print(f"  Manager: {site.manager.name if site.manager else 'N/A'}")
            print(f"  Status: {site.status}")
            
            print(f"\n  Budget Information:")
            print(f"  - Allocated Budget: NPR {site.allocated_budget:,.2f}")
            print(f"  - Material Cost: NPR {material_cost:,.2f}")
            print(f"  - Labor Cost: NPR {labor_cost:,.2f}")
            print(f"  - Other Expenses: NPR {other_expenses:,.2f}")
            print(f"  - Total Actual Spend: NPR {actual_spend:,.2f}")
            print(f"  - Remaining Budget: NPR {remaining_budget:,.2f}")
            print(f"  - Budget Usage: {budget_percentage:.1f}%")
            
            # Determine budget health
            if budget_percentage < 80:
                health = "🟢 GREEN (Healthy)"
            elif budget_percentage < 100:
                health = "🟡 YELLOW (Warning)"
            else:
                health = "🔴 RED (Over Budget)"
            print(f"  - Budget Health: {health}")
            
            print(f"\n  Timeline:")
            print(f"  - Start Date: {site.start_date}")
            print(f"  - Estimated End: {site.estimated_end_date or 'N/A'}")
            print(f"  - Actual End: {site.actual_end_date or 'N/A'}")
            
            print(f"\n✅ Report generation successful for {site.name}")
            
        except Exception as e:
            print(f"\n❌ Error generating report for {site.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    test_site_report()
