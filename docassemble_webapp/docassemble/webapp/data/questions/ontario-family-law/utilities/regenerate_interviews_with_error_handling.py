#!/usr/bin/env python3
"""
Regenerate all interviews with comprehensive error handling
"""

import sys
import os
from pathlib import Path
import logging
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from structured_interview_generator import StructuredInterviewGenerator
from error_handling_template import integrate_error_handling

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_existing_interviews():
    """Backup existing generated interviews"""
    source_dir = Path('workflow_output/structured_interviews')
    backup_dir = Path(f'workflow_output/structured_interviews_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    if source_dir.exists():
        shutil.copytree(source_dir, backup_dir)
        logger.info(f"Backed up existing interviews to {backup_dir}")
        return backup_dir
    return None

def update_existing_interviews():
    """Update existing generated interviews with error handling"""
    interviews_dir = Path('generated_interviews')
    updated_count = 0
    
    if interviews_dir.exists():
        for yml_file in interviews_dir.glob('*.yml'):
            try:
                logger.info(f"Updating {yml_file.name} with error handling...")
                
                # Read existing content
                with open(yml_file, 'r') as f:
                    content = f.read()
                
                # Integrate error handling
                updated_content = integrate_error_handling(content)
                
                # Save updated content
                with open(yml_file, 'w') as f:
                    f.write(updated_content)
                
                updated_count += 1
                logger.info(f"✓ Updated {yml_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to update {yml_file.name}: {e}")
    
    return updated_count

def regenerate_all_interviews():
    """Regenerate all interviews with error handling"""
    logger.info("Starting interview regeneration with error handling...")
    
    # Backup existing interviews
    backup_dir = backup_existing_interviews()
    
    # Create new generator
    generator = StructuredInterviewGenerator()
    
    # Generate all interviews (now with error handling built-in)
    count = generator.generate_all_interviews()
    
    logger.info(f"Generated {count} interviews with error handling")
    
    # Also update the existing generated_interviews directory
    updated = update_existing_interviews()
    logger.info(f"Updated {updated} existing interviews")
    
    return count, updated

def create_error_handling_index():
    """Create an index that includes error handling documentation"""
    index_content = """---
metadata:
  title: Ontario Family Law Forms with Error Handling
  short title: Forms Index
  description: Enhanced interviews with comprehensive error handling and debugging
---
modules:
  - .debug_helpers
---
features:
  debug: True
  question help button: True
---
objects:
  - error_log: DAList.using(object_type=DAObject, there_are_any=False)
---
mandatory: True
code: |
  intro_seen
  form_selection
  if form_selection == 'show_error_help':
    show_error_help
  else:
    selected_form
---
question: |
  Ontario Family Law Forms - Enhanced with Error Handling
subquestion: |
  This system provides comprehensive error handling and debugging features for all forms.
  
  ## Available Features:
  
  **Error Handling:**
  - Automatic error capture and logging
  - User-friendly validation messages
  - Debug mode for development
  - Session information tracking
  
  **Forms Available:**
  
  ### Financial Forms
  - [Form 13: Financial Statement (Support)](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/structured_interviews/form_13_interview.yml)
  - [Form 13.1: Financial Statement (Property)](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/structured_interviews/form_13.1_interview.yml)
  
  ### Application Forms
  - [Form 8: Application (General)](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/structured_interviews/form_8_interview.yml)
  - [Form 10: Answer](/interview?i=docassemble.webapp:ontario-family-law/utilities/workflow_output/structured_interviews/form_10_interview.yml)
  
  ### Debug Tools
  % if get_config('debug'):
  <div class="alert alert-info">
    <strong>Debug Mode Active</strong><br>
    Session: ${ user_info().session }<br>
    Errors Logged: ${ len(error_log) }
  </div>
  % endif
field: intro_seen
---
question: |
  Select an Action
fields:
  - "What would you like to do?": form_selection
    choices:
      - "Browse Forms": browse
      - "View Error Help": show_error_help
      - "Check System Status": status
---
event: show_error_help
question: |
  Error Handling Guide
subquestion: |
  ## How Error Handling Works
  
  All interviews in this system include:
  
  1. **Automatic Error Capture**: Any errors are automatically logged
  2. **Validation Messages**: Clear messages for invalid input
  3. **Debug Information**: Detailed error info when debug mode is enabled
  4. **Recovery Options**: Ability to go back and correct errors
  
  ## Common Error Types
  
  - **Required Fields**: Fields that must be filled
  - **Date Validation**: Proper date format required
  - **Number Validation**: Numeric values only
  - **Email Validation**: Valid email format
  
  ## Debug Mode
  
  To enable debug mode, add `?debug=1` to the interview URL.
buttons:
  - "Back to Index": restart
---
event: selected_form
question: |
  Form Selected
subquestion: |
  Redirecting to your selected form...
  
  All forms include comprehensive error handling.
buttons:
  - "Continue": continue
"""
    
    index_file = Path('generated_interviews/index_with_error_handling.yml')
    index_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_file, 'w') as f:
        f.write(index_content)
    
    logger.info(f"Created error handling index at {index_file}")
    return index_file

def main():
    """Main function to regenerate everything with error handling"""
    logger.info("=" * 60)
    logger.info("REGENERATING INTERVIEWS WITH ERROR HANDLING")
    logger.info("=" * 60)
    
    try:
        # Regenerate all interviews
        new_count, updated_count = regenerate_all_interviews()
        
        # Create the enhanced index
        index_file = create_error_handling_index()
        
        logger.info("=" * 60)
        logger.info("REGENERATION COMPLETE")
        logger.info(f"- New interviews generated: {new_count}")
        logger.info(f"- Existing interviews updated: {updated_count}")
        logger.info(f"- Index created at: {index_file}")
        logger.info("=" * 60)
        
        print("\n✅ All interviews now include comprehensive error handling!")
        print("\nError handling features added:")
        print("- Debug mode support")
        print("- Error capture and logging")
        print("- Field validation with user-friendly messages")
        print("- Session information tracking")
        print("- Error display screens")
        print("- Debug information screens")
        
    except Exception as e:
        logger.error(f"Failed to regenerate interviews: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()