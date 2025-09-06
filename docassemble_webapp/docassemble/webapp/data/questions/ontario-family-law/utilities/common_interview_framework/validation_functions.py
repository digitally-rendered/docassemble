"""
Validation Functions for Ontario Family Law Forms
Provides validation for common field types across all forms.
"""
import re
from docassemble.base.util import validation_error

def validate_ontario_postal_code(postal_code):
    """Validate Canadian postal code format"""
    if not postal_code:
        return True  # Optional field
    
    pattern = r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
    if not re.match(pattern, postal_code.strip()):
        validation_error("Please enter a valid Canadian postal code (format: A1A 1A1)")
    return True

def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Optional field
    
    # Remove all non-digits
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    else:
        validation_error("Please enter a valid 10-digit phone number")
    return True

def validate_court_file_number(file_number):
    """Validate Ontario court file number format"""
    if not file_number:
        return True  # Optional field
    
    # Remove spaces and convert to uppercase
    clean_number = file_number.replace(' ', '').replace('-', '').upper()
    
    # Should be format: XXYY followed by 8 digits
    pattern = r'^[A-Z]{2}\d{10}$'
    if not re.match(pattern, clean_number):
        validation_error("Please enter a valid court file number (format: XX-YY-12345678)")
    return True

def validate_email_address(email):
    """Validate email address format"""
    if not email:
        return True  # Optional field
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        validation_error("Please enter a valid email address")
    return True

def validate_currency_amount(amount):
    """Validate currency amount"""
    if not amount:
        return True  # Optional field
    
    try:
        float_amount = float(str(amount).replace('$', '').replace(',', ''))
        if float_amount < 0:
            validation_error("Amount cannot be negative")
        return True
    except ValueError:
        validation_error("Please enter a valid dollar amount")
    return True

def format_phone_number(phone):
    """Format phone number consistently"""
    if not phone:
        return ""
    
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return f"1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    
    return phone  # Return as-is if can't format

def format_postal_code(postal_code):
    """Format postal code consistently"""
    if not postal_code:
        return ""
    
    clean_code = postal_code.replace(' ', '').upper()
    if len(clean_code) == 6:
        return f"{clean_code[:3]} {clean_code[3:]}"
    
    return postal_code  # Return as-is if can't format

def format_court_file_number(file_number):
    """Format court file number consistently"""
    if not file_number:
        return ""
    
    clean_number = file_number.replace(' ', '').replace('-', '').upper()
    if len(clean_number) >= 10:
        return f"{clean_number[:2]}-{clean_number[2:4]}-{clean_number[4:]}"
    
    return file_number  # Return as-is if can't format
