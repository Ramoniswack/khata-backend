#!/usr/bin/env python
"""Check HR data and tenant assignment"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Department, Employee, Attendance
from tenants.models import Tenant
from users.models import User

def check_data():
    """Check HR data"""
    print("🔍 Checking HR data...\n")
    
    # Check tenants
    tenants = Tenant.objects.all()
    print(f"📊 Tenants: {tenants.count()}")
    for tenant in tenants:
        print(f"   - {tenant.name} (ID: {tenant.id})")
    
    # Check users
    users = User.objects.filter(is_superuser=True)
    print(f"\n👤 Superusers: {users.count()}")
    for user in users:
        print(f"   - {user.username} (Tenant: {user.tenant.name if user.tenant else 'None'})")
    
    # Check departments
    departments = Department.objects.all()
    print(f"\n🏢 Departments: {departments.count()}")
    for dept in departments:
        print(f"   - {dept.name} (Tenant: {dept.tenant.name})")
    
    # Check employees
    employees = Employee.objects.all()
    print(f"\n👥 Employees: {employees.count()}")
    for emp in employees[:5]:
        print(f"   - {emp.name} (Tenant: {emp.tenant.name}, Status: {emp.status})")
    
    # Check attendance
    attendance = Attendance.objects.all()
    print(f"\n📅 Attendance Records: {attendance.count()}")

if __name__ == "__main__":
    check_data()
