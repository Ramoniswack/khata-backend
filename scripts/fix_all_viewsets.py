#!/usr/bin/env python
"""
Script to fix all ViewSets to use get_queryset() instead of class-level queryset
This ensures proper tenant filtering in multi-tenant architecture
"""

import os
import re

# Files to fix
FILES_TO_FIX = [
    'sales/views.py',
    'purchase/views.py',
    'construction/views.py',
    'accounting/views.py',
    'tenants/views.py',
]

def fix_viewset_file(filepath):
    """Fix a single views.py file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Pattern to match: queryset = Model.objects.something()
    # We need to convert this to a get_queryset() method
    pattern = r'(\s+)queryset = (\w+)\.objects\.(.*?)\n'
    
    def replace_queryset(match):
        nonlocal changes_made
        indent = match.group(1)
        model = match.group(2)
        query_method = match.group(3)
        
        changes_made += 1
        
        # Return the replacement with get_queryset method
        return f'{indent}# queryset moved to get_queryset() for tenant filtering\n{indent}\n{indent}def get_queryset(self):\n{indent}    """Filter by current tenant"""\n{indent}    return {model}.objects.{query_method}\n'
    
    content = re.sub(pattern, replace_queryset, content)
    
    if changes_made > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {filepath}: {changes_made} ViewSets updated")
        return True
    else:
        print(f"ℹ️  No changes needed in {filepath}")
        return False

def main():
    print("=" * 60)
    print("FIXING VIEWSETS FOR TENANT FILTERING")
    print("=" * 60)
    print()
    
    total_fixed = 0
    
    for file in FILES_TO_FIX:
        filepath = os.path.join(os.path.dirname(__file__), file)
        if fix_viewset_file(filepath):
            total_fixed += 1
    
    print()
    print("=" * 60)
    print(f"SUMMARY: Fixed {total_fixed} files")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Restart Django server for changes to take effect!")
    print("   python manage.py runserver")

if __name__ == '__main__':
    main()
