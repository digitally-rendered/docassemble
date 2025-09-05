#!/usr/bin/env python3
"""
Smart Field Extractor for Ontario Family Law Forms
Distinguishes between actual form fields and explanatory text
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SmartFieldExtractor:
    """Extract only actual fillable fields from forms, not explanatory text"""
    
    # Patterns that indicate actual form fields
    FIELD_PATTERNS = [
        r'_+',  # Underscores indicate fill-in blanks
        r'\[\s*\]',  # Empty brackets for checkboxes
        r'☐|☑|□|■',  # Unicode checkboxes
        r'\(\s*\)',  # Empty parentheses for filling
        r':\s*$',  # Label ending with colon and whitespace
        r':\s*_+',  # Label with colon followed by underscores
        r'Date:\s*_+',  # Date fields
        r'Name:\s*_+',  # Name fields
        r'Address:\s*_+',  # Address fields
        r'\$\s*_+',  # Currency fields
        r'Amount:\s*_+',  # Amount fields
    ]
    
    # Patterns that indicate explanatory text, not fields
    EXPLANATORY_PATTERNS = [
        r'^(NOTE|NOTES|IMPORTANT|WARNING|CAUTION|NOTICE|INSTRUCTIONS?):',
        r'^(You must|You should|You can|You may|You are|You have|You will)',
        r'^(If you|If the|If your|When you|Before you|After you)',
        r'^(The court|The judge|The applicant|The respondent)',
        r'^(This form|This document|This section|This interview)',
        r'^(Complete this|Fill out|Provide|Include|Attach|Submit)',
        r'^(Pursuant to|According to|Under the|As per)',
        r'(Guidelines|Act|Regulation|Rule|Law|Code)',
        r'(must be|should be|can be|may be|will be)',
        r'^\d+\.',  # Numbered instructions
        r'^[a-z]\)',  # Lettered sub-items
        r'•',  # Bullet points
    ]
    
    # Common field labels in Ontario family law forms
    KNOWN_FIELD_LABELS = [
        'Court File Number',
        'Court Name',
        'Court Office Address',
        'Applicant',
        'Respondent',
        'Lawyer',
        'Full Legal Name',
        'First Name',
        'Last Name',
        'Middle Name',
        'Date of Birth',
        'Address',
        'Street',
        'City',
        'Province',
        'Postal Code',
        'Phone Number',
        'Email Address',
        'SIN',
        'Monthly Income',
        'Annual Income',
        'Expenses',
        'Assets',
        'Debts',
        'Date of Marriage',
        'Date of Separation',
        'Number of Children',
        'Child\'s Name',
        'Child\'s Date of Birth',
    ]
    
    def __init__(self):
        self.field_counter = 0
        
    def is_likely_field(self, text: str) -> bool:
        """Determine if text represents an actual form field"""
        if not text or len(text) < 3:
            return False
            
        # Check if it's clearly explanatory text
        for pattern in self.EXPLANATORY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check if it matches field patterns
        for pattern in self.FIELD_PATTERNS:
            if re.search(pattern, text):
                return True
        
        # Check against known field labels
        text_lower = text.lower().strip()
        for label in self.KNOWN_FIELD_LABELS:
            if label.lower() in text_lower:
                return True
        
        # Check length - very long text is usually explanatory
        if len(text) > 100:
            return False
        
        # Check for field-like endings
        if text.strip().endswith(':'):
            return True
        
        return False
    
    def extract_field_info(self, text: str) -> Optional[Dict]:
        """Extract field information from text"""
        if not self.is_likely_field(text):
            return None
        
        # Clean the text
        text = text.strip()
        
        # Remove field markers to get the label
        label = text
        label = re.sub(r'_+', '', label)
        label = re.sub(r'\[\s*\]', '', label)
        label = re.sub(r'[☐☑□■]', '', label)
        label = re.sub(r'\(\s*\)', '', label)
        label = re.sub(r':\s*$', '', label)
        label = label.strip()
        
        if not label or len(label) < 2:
            return None
        
        # Determine field type
        field_type = self.determine_field_type(text, label)
        
        # Create field dictionary
        field = {
            'field_id': f'field_{self.field_counter}',
            'field_label': label,
            'field_type': field_type,
            'required': self.is_required_field(text, label),
        }
        
        self.field_counter += 1
        return field
    
    def determine_field_type(self, text: str, label: str) -> str:
        """Determine the type of field"""
        text_lower = text.lower()
        label_lower = label.lower()
        
        # Check for specific field types
        if any(word in label_lower for word in ['date', 'born', 'birth', 'marriage', 'separation']):
            return 'date'
        elif any(word in label_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in label_lower for word in ['phone', 'telephone', 'fax', 'mobile', 'cell']):
            return 'phone'
        elif any(word in label_lower for word in ['amount', 'income', 'expense', 'cost', 'price', 'payment', 'money', 'dollar', '$']):
            return 'currency'
        elif any(word in label_lower for word in ['number of', 'how many', 'count', 'quantity']):
            return 'number'
        elif any(word in label_lower for word in ['postal code', 'zip']):
            return 'postal_code'
        elif any(word in label_lower for word in ['sin', 'social insurance']):
            return 'sin'
        elif re.search(r'\[\s*\]|[☐☑□■]', text):
            return 'checkbox'
        elif any(word in label_lower for word in ['address', 'street', 'city', 'province']):
            return 'address'
        elif any(word in label_lower for word in ['name', 'applicant', 'respondent']):
            return 'name'
        else:
            return 'text'
    
    def is_required_field(self, text: str, label: str) -> bool:
        """Determine if field is required"""
        # Court file number and names are usually required
        label_lower = label.lower()
        if any(word in label_lower for word in ['court file', 'name', 'applicant', 'respondent']):
            return True
        
        # Check for required indicators in surrounding text
        if '*' in text or '(required)' in text.lower() or '(mandatory)' in text.lower():
            return True
        
        return False
    
    def extract_fields_from_lines(self, lines: List[str]) -> List[Dict]:
        """Extract fields from a list of text lines"""
        fields = []
        
        for line in lines:
            if not line or not line.strip():
                continue
            
            # Try to extract field info
            field_info = self.extract_field_info(line)
            if field_info:
                fields.append(field_info)
                logger.debug(f"Extracted field: {field_info['field_label']}")
            else:
                # Log what we're skipping
                if len(line.strip()) > 10:
                    logger.debug(f"Skipped text (not a field): {line[:50]}...")
        
        return fields
    
    def extract_fields_from_tables(self, tables: List[List[List[str]]]) -> List[Dict]:
        """Extract fields from table structures"""
        fields = []
        
        for table in tables:
            for row in table:
                for cell in row:
                    if not cell or not cell.strip():
                        continue
                    
                    # Check if this cell looks like a field
                    field_info = self.extract_field_info(cell)
                    if field_info:
                        fields.append(field_info)
                        logger.debug(f"Extracted field from table: {field_info['field_label']}")
        
        return fields

def test_extractor():
    """Test the smart field extractor"""
    extractor = SmartFieldExtractor()
    
    test_texts = [
        "Court File Number: _______________",  # Should be a field
        "Applicant's Name: _______________",  # Should be a field
        "Date of Birth: ___/___/____",  # Should be a field
        "Monthly Income: $__________",  # Should be a field
        "☐ I agree to the terms",  # Should be a checkbox field
        "NOTE: You must complete this form if you are making a claim",  # Should NOT be a field
        "If you have income that is not shown in Part I",  # Should NOT be a field
        "Pursuant to the Child Support Guidelines",  # Should NOT be a field
        "This form must be filed within 30 days",  # Should NOT be a field
        "Email: _______________",  # Should be a field
    ]
    
    print("Testing Smart Field Extractor:\n")
    for text in test_texts:
        field_info = extractor.extract_field_info(text)
        if field_info:
            print(f"✓ FIELD: {text[:40]}...")
            print(f"  -> Label: {field_info['field_label']}")
            print(f"  -> Type: {field_info['field_type']}")
        else:
            print(f"✗ TEXT: {text[:40]}... (not a field)")
        print()

if __name__ == "__main__":
    test_extractor()