#!/usr/bin/env python3
"""
Fix Generated Docassemble YAML Files
Corrects common issues with generated interview files
"""

import re
from pathlib import Path
from typing import List

def fix_yaml_file(file_path: str) -> str:
    """Fix common YAML issues in a docassemble interview file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a question block with truncated text
        if line.strip() == 'question: |':
            fixed_lines.append(line)
            i += 1
            
            # Get the question text
            if i < len(lines):
                question_text = lines[i].strip()
                
                # If the text appears truncated (doesn't end with proper punctuation)
                if question_text and not question_text[-1] in '.?!:)"]':
                    # Complete the question text
                    if len(question_text) > 80:
                        question_text = question_text[:80] + '...'
                    question_text = question_text.replace('\n', ' ')
                
                fixed_lines.append(f"  {question_text}")
                i += 1
        
        # Check for field labels that are too long or truncated
        elif line.strip().startswith('- "') and '": ' in line:
            # Extract field label and variable
            match = re.match(r'^(\s*)-\s*"([^"]+)":\s*(.+)$', line)
            if match:
                indent, label, var_name = match.groups()
                
                # Fix truncated labels
                if label and not label[-1] in '.?!:)"]':
                    if len(label) > 80:
                        label = label[:77] + '...'
                
                # Ensure label doesn't have line breaks
                label = label.replace('\n', ' ').replace('\r', '')
                
                # Fix overly long variable names
                if len(var_name) > 60:
                    # Shorten variable name
                    parts = var_name.split('.')
                    if len(parts) > 1:
                        # Keep object prefix and shorten field name
                        prefix = parts[0]
                        field = '_'.join(parts[1].split('_')[:3])
                        var_name = f"{prefix}.{field}"
                    else:
                        # Just shorten the field name
                        var_name = '_'.join(var_name.split('_')[:5])[:50]
                
                fixed_lines.append(f'{indent}- "{label}": {var_name}')
            else:
                fixed_lines.append(line)
        
        # Fix variable names in mandatory code block that are too long
        elif re.match(r'^\s+\w+', line) and len(line.strip()) > 100:
            indent = len(line) - len(line.lstrip())
            var_name = line.strip()
            
            # Shorten variable name
            if '.' in var_name:
                parts = var_name.split('.')
                if len(parts) > 1:
                    prefix = parts[0]
                    field = '_'.join(parts[1].split('_')[:3])[:30]
                    var_name = f"{prefix}.{field}"
            else:
                var_name = '_'.join(var_name.split('_')[:5])[:50]
            
            fixed_lines.append(' ' * indent + var_name)
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Join lines back together
    fixed_content = '\n'.join(fixed_lines)
    
    # Additional fixes
    # Remove duplicate variable references in mandatory block
    fixed_content = remove_duplicate_variables(fixed_content)
    
    # Fix template variable references
    fixed_content = fix_template_variables(fixed_content)
    
    return fixed_content

def remove_duplicate_variables(content: str) -> str:
    """Remove duplicate variable references in mandatory code block"""
    
    lines = content.split('\n')
    fixed_lines = []
    seen_vars = set()
    in_mandatory = False
    
    for line in lines:
        if 'mandatory: True' in line:
            in_mandatory = True
            fixed_lines.append(line)
        elif line.startswith('---'):
            in_mandatory = False
            seen_vars = set()
            fixed_lines.append(line)
        elif in_mandatory and line.strip() and not line.strip().startswith('#'):
            # Check if this is a variable reference
            var_match = re.match(r'^(\s+)(\w+(?:\.\w+)*)\s*$', line)
            if var_match:
                indent, var_name = var_match.groups()
                if var_name in seen_vars:
                    # Comment out duplicate
                    fixed_lines.append(f"{indent}# {var_name}  # Duplicate removed")
                else:
                    seen_vars.add(var_name)
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_template_variables(content: str) -> str:
    """Fix template variable references"""
    
    # Fix form_name references
    content = content.replace("${form_name.replace('_', ' ').title()}", "Ontario Family Law Form")
    
    # Fix undefined method calls in templates
    content = re.sub(r'\$\{(\w+)\.name\.full\(\)\s+if\s+defined\([\'"](\w+)\.name\.first[\'"]?\)\s+else\s+[\'"]Not provided[\'"]?\}',
                     r'${showifdef("\1.name.first", \1.name.full())}', content)
    
    content = re.sub(r'\$\{(\w+)\.address\.on_one_line\(\)\s+if\s+defined\([\'"](\w+)\.address\.address[\'"]?\)\s+else\s+[\'"]Not provided[\'"]?\}',
                     r'${showifdef("\1.address.address", \1.address.on_one_line())}', content)
    
    return content

def process_directory(dir_path: str):
    """Process all YAML files in a directory"""
    
    dir_path = Path(dir_path)
    yaml_files = list(dir_path.glob('*.yml')) + list(dir_path.glob('*.yaml'))
    
    fixed_dir = dir_path / 'fixed'
    fixed_dir.mkdir(exist_ok=True)
    
    print(f"Processing {len(yaml_files)} files...")
    
    for file_path in yaml_files:
        print(f"  Fixing: {file_path.name}")
        
        try:
            # Fix the file
            fixed_content = fix_yaml_file(str(file_path))
            
            # Save fixed version
            fixed_path = fixed_dir / file_path.name
            with open(fixed_path, 'w') as f:
                f.write(fixed_content)
            
            print(f"    ✓ Saved to: fixed/{file_path.name}")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"\n✓ Fixed files saved to: {fixed_dir.absolute()}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    else:
        dir_path = "docassemble_interviews"
    
    print("=" * 60)
    print("FIXING DOCASSEMBLE YAML FILES")
    print("=" * 60)
    
    process_directory(dir_path)

if __name__ == "__main__":
    main()