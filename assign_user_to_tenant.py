"""
Quick script to assign a user to a tenant
Run with: python manage.py shell < assign_user_to_tenant.py
"""

from users.models import User
from tenants.models import Tenant

# Get the first user (usually the admin)
user = User.objects.first()

if not user:
    print("No users found in database!")
    exit()

print(f"Found user: {user.username} (ID: {user.id})")

# Check if user already has a tenant
if user.tenant:
    print(f"User already assigned to tenant: {user.tenant.name}")
else:
    # Get or create a tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Default Organization",
        defaults={
            'business_type': 'retail',
            'plan_type': 'free',
            'is_active': True,
            'active_modules': ['inventory', 'sales', 'purchase', 'accounting', 'reports']
        }
    )
    
    if created:
        print(f"Created new tenant: {tenant.name} (slug: {tenant.slug})")
    else:
        print(f"Using existing tenant: {tenant.name} (slug: {tenant.slug})")
    
    # Assign user to tenant
    user.tenant = tenant
    
    # Make user admin if they're not already
    if user.role == 'viewer' or not user.role:
        user.role = 'admin'
        print(f"Set user role to: admin")
    
    user.save()
    print(f"✓ Successfully assigned {user.username} to {tenant.name}")

print("\nDone! You can now access the users page.")
