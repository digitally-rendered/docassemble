#!/usr/bin/env python3
"""
Validate Docassemble YAML Interview Files
Checks syntax, structure, and docassemble-specific requirements
"""

import yaml
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

class DocassembleValidator:
    """Validate docassemble YAML interview files"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.required_sections = ['metadata']
        self.recommended_sections = ['objects', 'mandatory', 'question']
        
    def validate_yaml_syntax(self, file_path: str) -> bool:
        """Check if YAML syntax is valid"""
        try:
            with open(file_path, 'r') as f:
                documents = list(yaml.safe_load_all(f))
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
    
    def validate_docassemble_structure(self, file_path: str) -> bool:
        """Check docassemble-specific structure requirements"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Split by --- to get blocks
            blocks = content.split('---')
            
            # Check for metadata block
            has_metadata = False
            has_mandatory = False
            has_questions = False
            
            for block in blocks:
                if 'metadata:' in block:
                    has_metadata = True
                if 'mandatory:' in block:
                    has_mandatory = True
                if 'question:' in block:
                    has_questions = True
            
            if not has_metadata:
                self.errors.append("Missing metadata block")
            if not has_mandatory:
                self.warnings.append("No mandatory code block found")
            if not has_questions:
                self.warnings.append("No question blocks found")
            
            return has_metadata
            
        except Exception as e:
            self.errors.append(f"Error validating structure: {e}")
            return False
    
    def check_variable_references(self, file_path: str) -> List[str]:
        """Check for undefined variable references"""
        undefined_vars = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract defined variables from fields and code blocks
            defined_vars = set()
            
            # Find variables defined in fields
            field_pattern = r'^\s*-\s*["\']?([^"\':\s]+)["\']?\s*:\s*(\w+)'
            for match in re.finditer(field_pattern, content, re.MULTILINE):
                defined_vars.add(match.group(2))
            
            # Find variables in code blocks
            code_pattern = r'^\s*(\w+(?:\.\w+)*)\s*(?:=|\s)'
            for match in re.finditer(code_pattern, content, re.MULTILINE):
                defined_vars.add(match.group(1))
            
            # Find referenced variables
            ref_pattern = r'\$\{([^}]+)\}'
            for match in re.finditer(ref_pattern, content):
                var_name = match.group(1).split()[0].split('(')[0]
                if '.' in var_name:
                    base_var = var_name.split('.')[0]
                    if base_var not in defined_vars and base_var not in ['showifdef', 'defined']:
                        undefined_vars.append(var_name)
            
        except Exception as e:
            self.warnings.append(f"Could not check variable references: {e}")
        
        return undefined_vars
    
    def fix_common_issues(self, file_path: str) -> str:
        """Fix common issues in generated YAML files"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix long field names (docassemble has issues with very long variable names)
            def shorten_field_name(match):
                field_name = match.group(1)
                if len(field_name) > 50:
                    # Shorten to first 50 chars
                    words = field_name.split('_')[:5]
                    return f": {('_'.join(words))[:50]}"
                return match.group(0)
            
            content = re.sub(r':\s*(\w{51,})', shorten_field_name, content)
            
            # Fix duplicate variable definitions in mandatory code
            lines = content.split('\n')
            seen_vars = set()
            fixed_lines = []
            in_mandatory = False
            
            for line in lines:
                if 'mandatory: True' in line:
                    in_mandatory = True
                elif line.startswith('---'):
                    in_mandatory = False
                
                if in_mandatory and line.strip() and not line.strip().startswith('#'):
                    var_match = re.match(r'\s+(\w+(?:\.\w+)*)', line)
                    if var_match:
                        var_name = var_match.group(1)
                        if var_name in seen_vars:
                            fixed_lines.append(f"  # {line.strip()} # Duplicate removed")
                            continue
                        seen_vars.add(var_name)
                
                fixed_lines.append(line)
            
            return '\n'.join(fixed_lines)
            
        except Exception as e:
            self.errors.append(f"Error fixing issues: {e}")
            return content
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """Validate a single docassemble YAML file"""
        self.errors = []
        self.warnings = []
        
        print(f"\nValidating: {Path(file_path).name}")
        
        # Check YAML syntax
        if not self.validate_yaml_syntax(file_path):
            return False, self.errors, self.warnings
        
        # Check docassemble structure
        if not self.validate_docassemble_structure(file_path):
            return False, self.errors, self.warnings
        
        # Check for undefined variables
        undefined = self.check_variable_references(file_path)
        if undefined:
            self.warnings.append(f"Potentially undefined variables: {', '.join(undefined[:5])}")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def validate_directory(self, dir_path: str) -> Dict:
        """Validate all YAML files in a directory"""
        results = {
            'total': 0,
            'valid': 0,
            'errors': 0,
            'warnings': 0,
            'files': []
        }
        
        dir_path = Path(dir_path)
        yaml_files = list(dir_path.glob('*.yml')) + list(dir_path.glob('*.yaml'))
        
        results['total'] = len(yaml_files)
        
        for file_path in yaml_files:
            is_valid, errors, warnings = self.validate_file(str(file_path))
            
            file_result = {
                'name': file_path.name,
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings
            }
            
            results['files'].append(file_result)
            
            if is_valid:
                results['valid'] += 1
                print(f"  ✓ Valid")
            else:
                results['errors'] += 1
                print(f"  ✗ Invalid - {len(errors)} errors")
            
            if warnings:
                results['warnings'] += len(warnings)
                print(f"  ⚠ {len(warnings)} warnings")
            
            # Print errors and warnings
            for error in errors:
                print(f"    ERROR: {error}")
            for warning in warnings:
                print(f"    WARNING: {warning}")
        
        return results

def fix_interviews(dir_path: str):
    """Fix common issues in all interview files"""
    validator = DocassembleValidator()
    dir_path = Path(dir_path)
    yaml_files = list(dir_path.glob('*.yml')) + list(dir_path.glob('*.yaml'))
    
    fixed_count = 0
    
    for file_path in yaml_files:
        print(f"Fixing: {file_path.name}")
        
        # Fix common issues
        fixed_content = validator.fix_common_issues(str(file_path))
        
        # Save fixed version
        fixed_path = file_path.parent / f"fixed_{file_path.name}"
        with open(fixed_path, 'w') as f:
            f.write(fixed_content)
        
        fixed_count += 1
        print(f"  ✓ Fixed version saved as: fixed_{file_path.name}")
    
    return fixed_count

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    else:
        dir_path = "docassemble_interviews"
    
    print("=" * 60)
    print("DOCASSEMBLE INTERVIEW VALIDATOR")
    print("=" * 60)
    
    validator = DocassembleValidator()
    
    # Validate all files
    results = validator.validate_directory(dir_path)
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total files: {results['total']}")
    print(f"Valid files: {results['valid']}")
    print(f"Files with errors: {results['errors']}")
    print(f"Total warnings: {results['warnings']}")
    
    # If there are errors, offer to fix them
    if results['errors'] > 0 or results['warnings'] > 0:
        print("\nWould you like to fix common issues? (yes/no)")
        response = input().strip().lower()
        if response == 'yes' or response == 'y':
            fixed = fix_interviews(dir_path)
            print(f"\n✓ Fixed {fixed} files. Check the 'fixed_' versions.")

if __name__ == "__main__":
    main()