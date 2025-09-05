"""
Error Handling Template Generator for Docassemble Interviews
Provides reusable error handling patterns for generated interviews
"""

def generate_error_handling_includes():
    """Generate the includes section for error handling"""
    return """
modules:
  - .debug_helpers
  - docassemble.base.util
"""

def generate_error_handling_features():
    """Generate features for debugging and error handling"""
    return """
features:
  debug: True
  question help button: True
  question back button: True
  progress bar: True
  progress bar method: percentage
  progress bar multiplier: 1.5
"""

def generate_error_handling_objects():
    """Generate objects for error tracking"""
    return """
objects:
  - error_log: DAList.using(object_type=DAObject, there_are_any=False)
  - debug_info: DAObject
"""

def generate_error_handling_code():
    """Generate comprehensive error handling code blocks"""
    return """
---
# Initialize debug mode
code: |
  if not defined('debug_mode'):
    debug_mode = get_config('debug', False)
---
# Error capture function
code: |
  def capture_form_error(context="", field_name=""):
    '''Capture and log form validation errors'''
    from .debug_helpers import DebugHelper
    error_info = DebugHelper.capture_error()
    if error_info:
      error_entry = DAObject()
      error_entry.timestamp = current_datetime()
      error_entry.context = context
      error_entry.field = field_name
      error_entry.error = error_info
      error_log.append(error_entry)
      if debug_mode:
        log(f"Form error in {context}: {error_info['message']}", 'error')
    return error_info
---
# Safe field access wrapper
code: |
  def safe_get_field(obj, field_name, default=""):
    '''Safely access object fields with error handling'''
    try:
      if hasattr(obj, field_name):
        value = getattr(obj, field_name)
        return value if value is not None else default
      return default
    except Exception as e:
      capture_form_error(f"safe_get_field({field_name})", field_name)
      return default
---
# Validation error handler
code: |
  def handle_validation_error(field_name, value, validation_type=""):
    '''Handle field validation errors with user-friendly messages'''
    error_messages = {
      'required': f"The field '{field_name}' is required.",
      'date': f"Please enter a valid date for '{field_name}'.",
      'email': f"Please enter a valid email address for '{field_name}'.",
      'phone': f"Please enter a valid phone number for '{field_name}'.",
      'currency': f"Please enter a valid dollar amount for '{field_name}'.",
      'number': f"Please enter a valid number for '{field_name}'.",
      'percentage': f"Please enter a valid percentage for '{field_name}'.",
      'postal_code': f"Please enter a valid postal code for '{field_name}'."
    }
    
    message = error_messages.get(validation_type, f"Invalid value for '{field_name}': {value}")
    
    if debug_mode:
      log(f"Validation error: {message}", 'error')
      
    validation_errors.append({
      'field': field_name,
      'value': value,
      'type': validation_type,
      'message': message
    })
    
    return message
---
# Initialize validation errors list
code: |
  if not defined('validation_errors'):
    validation_errors = []
---
# Field validation wrapper
code: |
  def validate_field(field_name, value, validation_rules):
    '''Validate a field against multiple rules'''
    errors = []
    
    # Required field check
    if 'required' in validation_rules and validation_rules['required']:
      if not value or (isinstance(value, str) and not value.strip()):
        errors.append(handle_validation_error(field_name, value, 'required'))
    
    # Type-specific validation
    if value and 'type' in validation_rules:
      field_type = validation_rules['type']
      
      if field_type == 'date':
        try:
          # Validate date format
          if isinstance(value, str):
            from datetime import datetime
            datetime.strptime(value, '%Y-%m-%d')
        except:
          errors.append(handle_validation_error(field_name, value, 'date'))
      
      elif field_type == 'email':
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', str(value)):
          errors.append(handle_validation_error(field_name, value, 'email'))
      
      elif field_type == 'phone':
        import re
        phone_str = re.sub(r'[^0-9]', '', str(value))
        if len(phone_str) not in [10, 11]:
          errors.append(handle_validation_error(field_name, value, 'phone'))
      
      elif field_type == 'currency' or field_type == 'number':
        try:
          float(str(value).replace('$', '').replace(',', ''))
        except:
          errors.append(handle_validation_error(field_name, value, field_type))
    
    return errors
"""

def generate_error_display_questions():
    """Generate questions for displaying errors to users"""
    return """
---
# Error display screen
event: show_form_errors
question: |
  Form Validation Errors
subquestion: |
  % if len(validation_errors) > 0:
  <div class="alert alert-danger" role="alert">
    <h4 class="alert-heading">Please correct the following errors:</h4>
    <ul>
    % for error in validation_errors:
      <li><strong>${ error['field'] }:</strong> ${ error['message'] }</li>
    % endfor
    </ul>
  </div>
  % endif
  
  % if debug_mode and len(error_log) > 0:
  <details>
    <summary>Debug Information (${len(error_log)} errors logged)</summary>
    % for entry in error_log:
    <div class="card mb-2">
      <div class="card-body">
        <h6 class="card-title">Error at ${ entry.timestamp }</h6>
        <p class="card-text">
          <strong>Context:</strong> ${ entry.context }<br>
          <strong>Field:</strong> ${ entry.field }<br>
          <strong>Type:</strong> ${ entry.error['type'] }<br>
          <strong>Message:</strong> ${ entry.error['message'] }
        </p>
        % if debug_mode:
        <details>
          <summary>Stack Trace</summary>
          <pre>${ entry.error.get('formatted_exception', 'N/A') }</pre>
        </details>
        % endif
      </div>
    </div>
    % endfor
  </details>
  % endif
buttons:
  - "Go Back": restart
  - "Exit": exit
---
# Debug information screen
event: show_debug_info
question: |
  Debug Information
subquestion: |
  <div class="alert alert-info">
    <h4>Session Information</h4>
    <ul>
      <li><strong>Interview:</strong> ${ user_info().filename }</li>
      <li><strong>Session ID:</strong> ${ user_info().session }</li>
      <li><strong>Debug Mode:</strong> ${ debug_mode }</li>
      <li><strong>Errors Logged:</strong> ${ len(error_log) }</li>
      <li><strong>Validation Errors:</strong> ${ len(validation_errors) }</li>
    </ul>
  </div>
  
  % if defined('user_party'):
  <h4>User Information</h4>
  <ul>
    <li><strong>Name:</strong> ${ safe_get_field(user_party, 'name', 'Not provided') }</li>
    % if hasattr(user_party, 'email'):
    <li><strong>Email:</strong> ${ safe_get_field(user_party, 'email', 'Not provided') }</li>
    % endif
  </ul>
  % endif
  
  <h4>Form Progress</h4>
  <ul>
    % for var in ['intro_seen', 'user_party.name.first', 'other_party.name.first', 'children.gathered', 'review_complete']:
    <li><strong>${ var }:</strong> ${ 'Yes' if defined(var) else 'No' }</li>
    % endfor
  </ul>
buttons:
  - "Continue": continue
  - "Show Errors": show_form_errors
  - "Restart": restart
"""

def generate_error_handling_review():
    """Generate review screen with error handling"""
    return """
---
# Error-aware review screen
review:
  - note: |
      % if len(validation_errors) > 0:
      <div class="alert alert-warning">
        There are ${ len(validation_errors) } validation errors. Please review and correct them.
      </div>
      % endif
  - Edit: user_party.name.first
    button: |
      **Your Name:** ${ safe_get_field(user_party, 'name', 'Not provided') }
  - Edit: other_party.name.first
    button: |
      **Other Party:** ${ safe_get_field(other_party, 'name', 'Not provided') }
  - note: |
      % if debug_mode:
      <hr>
      <button type="button" class="btn btn-sm btn-secondary" onclick="window.location.href='${ url_action('show_debug_info') }'">
        Show Debug Info
      </button>
      % endif
"""

def generate_complete_error_handling_template():
    """Generate a complete error handling template for interviews"""
    template = []
    
    # Add sections with separators
    template.append("---")
    template.append("# ERROR HANDLING FRAMEWORK")
    template.append("# This section provides comprehensive error handling for the interview")
    
    template.append(generate_error_handling_includes())
    template.append("---")
    template.append(generate_error_handling_features())
    template.append("---")
    template.append(generate_error_handling_objects())
    template.append(generate_error_handling_code())
    template.append(generate_error_display_questions())
    template.append(generate_error_handling_review())
    
    return "\n".join(template)

def integrate_error_handling(existing_yaml_content):
    """Integrate error handling into existing YAML content"""
    lines = existing_yaml_content.split('\n')
    
    # Find insertion points
    metadata_end = -1
    includes_end = -1
    features_end = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if metadata_end == -1:
                metadata_end = i
            elif includes_end == -1 and any('include:' in lines[j] or 'modules:' in lines[j] 
                                           for j in range(metadata_end, i)):
                includes_end = i
            elif features_end == -1 and any('features:' in lines[j] 
                                           for j in range(metadata_end, i)):
                features_end = i
    
    # Build new content with error handling
    new_lines = []
    error_template = generate_complete_error_handling_template().split('\n')
    
    # Add metadata section
    if metadata_end > 0:
        new_lines.extend(lines[:metadata_end])
    
    # Add error handling sections
    for template_line in error_template:
        if template_line.strip() and not template_line.startswith('#'):
            new_lines.append(template_line)
    
    # Add rest of original content (skipping duplicate sections)
    start_idx = includes_end if includes_end > 0 else metadata_end
    for line in lines[start_idx:]:
        # Skip duplicate module/include declarations
        if not any(keyword in line for keyword in ['modules:', 'include:', 'features:', '.debug_helpers']):
            new_lines.append(line)
    
    return '\n'.join(new_lines)

if __name__ == "__main__":
    # Generate standalone error handling template
    template = generate_complete_error_handling_template()
    
    with open('error_handling_template.yml', 'w') as f:
        f.write(template)
    
    print("Error handling template generated successfully!")