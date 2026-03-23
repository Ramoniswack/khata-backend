#!/usr/bin/env python
"""Fix formatting issues in ViewSets"""
import re

files = ['sales/views.py', 'purchase/views.py', 'construction/views.py', 'tenants/views.py']

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the messy formatting from the automated script
        # Pattern: # queryset moved... followed by extra newlines and indented get_queryset
        pattern = r'    # queryset moved to get_queryset\(\) for tenant filtering\n\n    \n\n    def get_queryset\(self\):\n\n        """Filter by current tenant"""\n\n        return '
        replacement = '    def get_queryset(self):\n        """Filter by current tenant"""\n        return '
        
        content = re.sub(pattern, replacement, content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {filepath}")
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

print("\nDone!")
