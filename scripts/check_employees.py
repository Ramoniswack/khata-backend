#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee
from tenants.models import Tenant

t = Tenant.objects.first()
print(f'Tenant: {t.name}')
print(f'\nTotal employees: {Employee.objects.filter(tenant=t).count()}')
print(f'Active employees: {Employee.objects.filter(tenant=t, status="active").count()}')

print('\nAll employees:')
for emp in Employee.objects.filter(tenant=t):
    print(f'  - {emp.first_name} {emp.last_name} (Status: {emp.status})')
