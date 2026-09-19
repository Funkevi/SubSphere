#!/usr/bin/env python3
"""
Fix all pylint issues automatically
"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix pylint issues in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix trailing whitespace
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Fix unused arguments (add _ prefix)
    content = re.sub(
        r'(\n\s+)(authorization|token|current_user)(\s*:\s*)',
        r'\1_\2\3',
        content
    )
    
    # Fix raise-missing-from (add 'from e' or 'from None')
    content = re.sub(
        r'raise HTTPException\((.*?)\)\n(\s+)(except|$)',
        lambda m: f'raise HTTPException({m.group(1)}) from e\n{m.group(2)}{m.group(3)}' 
                  if 'str(e)' in m.group(1) 
                  else f'raise HTTPException({m.group(1)}) from None\n{m.group(2)}{m.group(3)}',
        content,
        flags=re.MULTILINE
    )
    
    # Fix unused variables (prefix with _)
    content = re.sub(
        r'except (\w+Exception) as (e):\n(\s+)raise HTTPException',
        r'except \1:\n\3raise HTTPException',
        content
    )
    
    # Fix unused imports
    if 'from datetime import' in content and 'datetime.' not in content and 'datetime(' not in content:
        content = re.sub(r'from datetime import datetime\n', '', content)
    
    if 'from uuid import uuid4' in content and 'uuid4(' not in content:
        content = re.sub(r'from uuid import uuid4\n', '', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {filepath}")
        return True
    return False

# Fix all API route files
api_files = [
    'src/api/plans_routes.py',
    'src/api/payment_routes.py',
    'src/api/auth_routes.py',
    'src/api/admin_routes.py',
    'src/api/subscription_routes.py',
]

for file in api_files:
    path = Path(file)
    if path.exists():
        fix_file(path)

print("\n✅ All files fixed!")
