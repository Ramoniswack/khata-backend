#!/usr/bin/env python
"""
Check user4's tenant and why it's not showing on /erp page
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant

def check_user4():
    print("=" * 80)
    print("CHECKING user4@test.com TENANT VISIBILITY")
    print("=" * 80)
    
    try:
        user4 = User.objects.get(email='user4@test.com')
        print(f"\n✓ user4@test.com found")
        print(f"  - ID: {user4.id}")
        print(f"  - Username: {user4.username}")
        print(f"  - Tenant: {user4.tenant}")
        print(f"  - Role: {user4.role}")
        
        if user4.tenant:
            tenant = user4.tenant
            print(f"\n✓ Tenant details:")
            print(f"  - ID: {tenant.id}")
            print(f"  - Name: {tenant.name}")
            print(f"  - Slug: {tenant.slug}")
            print(f"  - Created from registration: {tenant.created_from_registration}")
            print(f"  - Is active: {tenant.is_active}")
            print(f"  - Created by: {tenant.created_by}")
            
            # Check what the TenantViewSet would return
            print(f"\n" + "=" * 80)
            print("CHECKING TENANT VISIBILITY IN API")
            print("=" * 80)
            
            # Simulate TenantViewSet.get_queryset() logic
            # From backend/tenants/views.py:
            # return Tenant.objects.filter(
            #     Q(created_by=self.request.user) | Q(users=self.request.user)
            # ).exclude(created_from_registration=True).distinct()
            
            from django.db.models import Q
            
            # Check if user4 would see this tenant
            visible_tenants = Tenant.objects.filter(
                Q(created_by=user4) | Q(users=user4)
            ).exclude(created_from_registration=True).distinct()
            
            print(f"\n✓ Tenants visible to user4@test.com: {visible_tenants.count()}")
            for t in visible_tenants:
                print(f"  - {t.name} (ID: {t.id}, slug: {t.slug})")
            
            if tenant not in visible_tenants:
                print(f"\n✗ PROBLEM FOUND!")
                print(f"  Tenant '{tenant.name}' is NOT visible to user4@test.com")
                print(f"\n  Reasons:")
                
                if tenant.created_from_registration:
                    print(f"    ✗ Tenant has created_from_registration=True (HIDDEN)")
                else:
                    print(f"    ✓ Tenant has created_from_registration=False")
                
                is_creator = tenant.created_by == user4
                print(f"    {'✓' if is_creator else '✗'} User is creator: {is_creator}")
                
                is_member = user4 in tenant.users.all()
                print(f"    {'✓' if is_member else '✗'} User is member: {is_member}")
                
                print(f"\n  Solution:")
                if tenant.created_from_registration:
                    print(f"    Set created_from_registration=False on tenant '{tenant.name}'")
            else:
                print(f"\n✓ Tenant '{tenant.name}' IS visible to user4@test.com")
        else:
            print(f"\n✗ user4@test.com has NO tenant assigned!")
    
    except User.DoesNotExist:
        print("\n✗ user4@test.com not found!")
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    check_user4()
