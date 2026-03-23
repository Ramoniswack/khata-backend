#!/usr/bin/env python3
"""Fix indentation in sales_dashboard function"""

# Read the file
with open('sales/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the sales_dashboard function
in_function = False
function_start = None
function_end = None

for i, line in enumerate(lines):
    if 'def sales_dashboard(self, request):' in line:
        in_function = True
        function_start = i
        print(f"Found function start at line {i+1}")
    elif in_function and line.strip().startswith('def ') and 'sales_dashboard' not in line:
        function_end = i
        print(f"Found function end at line {i+1}")
        break
    elif in_function and line.strip().startswith('@extend_schema_view'):
        function_end = i
        print(f"Found function end at line {i+1}")
        break

if function_start is not None and function_end is not None:
    # Fix indentation in the function
    fixed_lines = []
    base_indent = 8  # 2 levels of indentation (class + method)
    
    for i in range(function_start, function_end):
        line = lines[i]
        stripped = line.lstrip()
        
        if not stripped or stripped.startswith('#'):
            # Keep empty lines and comments with proper indentation
            if stripped.startswith('#'):
                fixed_lines.append(' ' * base_indent + stripped)
            else:
                fixed_lines.append(line)
        elif 'def sales_dashboard' in line:
            # Keep function definition as is
            fixed_lines.append(line)
        elif stripped.startswith('"""'):
            # Docstring
            fixed_lines.append(' ' * base_indent + stripped)
        elif stripped.startswith('from ') or stripped.startswith('import '):
            # Imports inside function
            fixed_lines.append(' ' * base_indent + stripped)
        elif stripped.startswith('tenant =') or stripped.startswith('period ='):
            # Variable assignments at function level
            fixed_lines.append(' ' * base_indent + stripped)
        elif stripped.startswith('if ') or stripped.startswith('elif ') or stripped.startswith('else'):
            # Control flow at function level
            fixed_lines.append(' ' * base_indent + stripped)
        elif stripped.startswith('return '):
            # Return statement
            fixed_lines.append(' ' * base_indent + stripped)
        else:
            # Everything else - try to determine proper indentation
            # Count leading spaces in original
            original_indent = len(line) - len(stripped)
            
            # If it's way too indented, reduce it
            if original_indent > base_indent + 12:
                # Probably inside a nested block
                fixed_lines.append(' ' * (base_indent + 4) + stripped)
            elif original_indent > base_indent:
                # Keep relative indentation
                fixed_lines.append(line)
            else:
                # Add base indentation
                fixed_lines.append(' ' * base_indent + stripped)
    
    # Write back
    with open('sales/views.py', 'w', encoding='utf-8') as f:
        f.writelines(lines[:function_start])
        f.writelines(fixed_lines)
        f.writelines(lines[function_end:])
    
    print(f"Fixed indentation for {len(fixed_lines)} lines")
else:
    print("Could not find function boundaries")
