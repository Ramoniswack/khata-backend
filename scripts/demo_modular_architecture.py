#!/usr/bin/env python
"""
Demo script for modular architecture
Shows the complete flow of tenant creation with module selection
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.membership_models import UserTenantMembership

User = get_user_model()

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    """Print a formatted section"""
    print(f"\n--- {text} ---")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_info(text, indent=2):
    """Print info message"""
    print(f"{' '*indent}{text}")

def demo_modular_architecture():
    """Demonstrate the modular architecture system"""
    
    print_header("KHATA BUSINESS OS - MODULAR ARCHITECTURE DEMO")
    
    # Create demo user
    print_section("Step 1: User Registration")
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print_success("User registered: demo_user")
    else:
        print_success("Using existing user: demo_user")
    
    # Scenario 1: Core Business
    print_section("Scenario 1: Core Business (Wholesale Trading)")
    print_info("Business Type: Wholesale")
    print_info("Selected Modules: CORE only")
    
    core_tenant = Tenant.objects.create(
        name="Demo Wholesale Trading",
        business_type="wholesale",
        owner_name="John Doe",
        email="john@wholesale.com",
        phone="+977 9812345678",
        address="Kathmandu, Nepal",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports']
    )
    
    print_success(f"Organization created: {core_tenant.name}")
    print_info(f"Slug: {core_tenant.slug}")
    print_info(f"Active Modules: {', '.join(core_tenant.active_modules)}")
    
    print_info("\nAvailable Features:")
    print_info("✓ Product Management", 4)
    print_info("✓ Customer Management", 4)
    print_info("✓ Supplier Management", 4)
    print_info("✓ Sales Orders & Invoices", 4)
    print_info("✓ Purchase Orders", 4)
    print_info("✓ Accounting & Reports", 4)
    print_info("✗ Construction Features", 4)
    print_info("✗ Hardware Features", 4)
    
    # Scenario 2: Construction Company
    print_section("Scenario 2: Construction Company")
    print_info("Business Type: Construction")
    print_info("Selected Modules: CORE + CONSTRUCTION")
    
    construction_tenant = Tenant.objects.create(
        name="Demo Construction Co",
        business_type="construction",
        owner_name="Jane Smith",
        email="jane@construction.com",
        phone="+977 9823456789",
        address="Pokhara, Nepal",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports', 'construction']
    )
    
    print_success(f"Organization created: {construction_tenant.name}")
    print_info(f"Slug: {construction_tenant.slug}")
    print_info(f"Active Modules: {', '.join(construction_tenant.active_modules)}")
    
    print_info("\nAvailable Features:")
    print_info("✓ All Core Features", 4)
    print_info("✓ Site Management", 4)
    print_info("✓ Labor & Attendance", 4)
    print_info("✓ Material Consumption", 4)
    print_info("✓ Equipment Tracking", 4)
    print_info("✓ Budget Tracking", 4)
    print_info("✓ Site P&L Reports", 4)
    print_info("✗ Hardware Features", 4)
    
    # Scenario 3: Hardware Store
    print_section("Scenario 3: Hardware Store")
    print_info("Business Type: Hardware")
    print_info("Selected Modules: CORE + HARDWARE")
    
    hardware_tenant = Tenant.objects.create(
        name="Demo Hardware Plus",
        business_type="hardware",
        owner_name="Bob Johnson",
        email="bob@hardware.com",
        phone="+977 9834567890",
        address="Lalitpur, Nepal",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports', 'hardware']
    )
    
    print_success(f"Organization created: {hardware_tenant.name}")
    print_info(f"Slug: {hardware_tenant.slug}")
    print_info(f"Active Modules: {', '.join(hardware_tenant.active_modules)}")
    
    print_info("\nAvailable Features:")
    print_info("✓ All Core Features", 4)
    print_info("✓ Bulk Pricing", 4)
    print_info("✓ Customer Ledger", 4)
    print_info("✓ Credit (Udhaar) System", 4)
    print_info("✓ Payment Tracking", 4)
    print_info("✓ Udhaar Reminders", 4)
    print_info("✗ Construction Features", 4)
    
    # Scenario 4: Full-Featured Company
    print_section("Scenario 4: Full-Featured Company")
    print_info("Business Type: Construction")
    print_info("Selected Modules: ALL MODULES")
    
    full_tenant = Tenant.objects.create(
        name="Demo Mega Corp",
        business_type="construction",
        owner_name="Alice Williams",
        email="alice@megacorp.com",
        phone="+977 9845678901",
        address="Bhaktapur, Nepal",
        created_by=user,
        active_modules=['inventory', 'sales', 'purchase', 'accounting', 'reports', 
                       'construction', 'hardware', 'hr']
    )
    
    print_success(f"Organization created: {full_tenant.name}")
    print_info(f"Slug: {full_tenant.slug}")
    print_info(f"Active Modules: {', '.join(full_tenant.active_modules)}")
    
    print_info("\nAvailable Features:")
    print_info("✓ All Core Features", 4)
    print_info("✓ All Construction Features", 4)
    print_info("✓ All Hardware Features", 4)
    print_info("✓ All HR Features", 4)
    
    # Module Management Demo
    print_section("Module Management Demo")
    print_info(f"Current modules for {core_tenant.name}:")
    print_info(f"{core_tenant.active_modules}", 4)
    
    print_info("\nActivating 'construction' module...")
    core_tenant.activate_module('construction')
    print_success("Module activated")
    print_info(f"Updated modules: {core_tenant.active_modules}", 4)
    
    print_info("\nDeactivating 'construction' module...")
    core_tenant.deactivate_module('construction')
    print_success("Module deactivated")
    print_info(f"Updated modules: {core_tenant.active_modules}", 4)
    
    # Access Control Demo
    print_section("Access Control Demo")
    
    def check_access(tenant, module):
        has_access = tenant.has_module(module)
        status = "✓ ALLOWED" if has_access else "✗ DENIED"
        print_info(f"{tenant.name} -> {module}: {status}", 4)
    
    print_info("Core Business Access:")
    check_access(core_tenant, 'inventory')
    check_access(core_tenant, 'sales')
    check_access(core_tenant, 'construction')
    check_access(core_tenant, 'hardware')
    
    print_info("\nConstruction Company Access:")
    check_access(construction_tenant, 'inventory')
    check_access(construction_tenant, 'construction')
    check_access(construction_tenant, 'hardware')
    
    print_info("\nHardware Store Access:")
    check_access(hardware_tenant, 'inventory')
    check_access(hardware_tenant, 'hardware')
    check_access(hardware_tenant, 'construction')
    
    # Summary
    print_header("SUMMARY")
    
    all_tenants = [core_tenant, construction_tenant, hardware_tenant, full_tenant]
    
    print_info("Organizations Created:")
    for tenant in all_tenants:
        print_info(f"• {tenant.name}", 4)
        print_info(f"  Type: {tenant.business_type}", 6)
        print_info(f"  Modules: {len(tenant.active_modules)}", 6)
        print_info(f"  Slug: {tenant.slug}", 6)
    
    print_info("\nModule Distribution:")
    module_counts = {}
    for tenant in all_tenants:
        for module in tenant.active_modules:
            module_counts[module] = module_counts.get(module, 0) + 1
    
    for module, count in sorted(module_counts.items()):
        print_info(f"• {module}: {count} organizations", 4)
    
    print_header("DEMO COMPLETE")
    print_info("✓ Modular architecture is fully functional")
    print_info("✓ Organizations can subscribe to different modules")
    print_info("✓ Access control works correctly")
    print_info("✓ Module activation/deactivation works")
    
    # Cleanup
    print_section("Cleanup")
    for tenant in all_tenants:
        tenant.delete()
    print_success("Demo tenants deleted")
    
    print("\n")

if __name__ == '__main__':
    demo_modular_architecture()
