#!/usr/bin/env python3
"""
Content Classifier for Ontario Family Law Forms
Classifies content as fields, instructions, headings, or legal text
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content in forms"""
    FIELD = "field"                    # Actual fillable field
    INSTRUCTION = "instruction"        # Instructions for filling out the form
    HEADING = "heading"               # Section headings
    LEGAL_TEXT = "legal_text"         # Legal notices, warnings, disclaimers
    HELP_TEXT = "help_text"           # Help or guidance text
    LABEL = "label"                   # Field label (associated with a field)
    CHECKBOX_OPTION = "checkbox_option"  # Option in a checkbox group
    TABLE_HEADER = "table_header"     # Table column headers
    EXAMPLE = "example"               # Example text showing how to fill something

class ContentClassifier:
    """Classify different types of content in forms"""
    
    # Patterns for different content types
    FIELD_INDICATORS = [
        r'_{3,}',                        # Three or more underscores
        r'\[[\s]*\]',                    # Empty brackets (checkbox)
        r'☐|□',                          # Checkbox symbols
        r'\(\s*\)',                      # Empty parentheses
        r':\s*_{2,}',                    # Colon followed by underscores
        r'Date:\s*___/___/____',         # Date format
        r'\$\s*_{3,}',                   # Currency field
    ]
    
    INSTRUCTION_INDICATORS = [
        r'^(Complete|Fill out|Fill in|Provide|Enter|Include|Attach|Submit|Sign)',
        r'^(Please|You must|You should|You may|You can|You will need)',
        r'^(Do not|Don\'t|Make sure|Ensure|Remember|Be sure)',
        r'(following information|following documents|information below)',
        r'^Step \d+:',
        r'^Instructions?:',
    ]
    
    LEGAL_TEXT_INDICATORS = [
        r'^(NOTE|NOTES|IMPORTANT|WARNING|CAUTION|NOTICE|ATTENTION):',
        r'(Pursuant to|According to|Under the|As per|In accordance with)',
        r'(Act|Regulation|Rule|Law|Code|Guidelines|Statute)',
        r'(shall|shall not|must|must not|may|may not) be',
        r'(legal|legally|lawful|unlawful|prohibited)',
        r'(penalty|penalties|fine|imprisonment|offense)',
    ]
    
    HEADING_INDICATORS = [
        r'^PART \d+:',
        r'^Section [A-Z0-9]+:',
        r'^Schedule [A-Z]:',
        r'^[A-Z][A-Z\s]+$',  # All caps line
        r'^\d+\.\s+[A-Z]',   # Numbered section with capital
        r'^[A-Z][\w\s]{2,30}:$',  # Short title ending with colon
    ]
    
    HELP_TEXT_INDICATORS = [
        r'^\(.*\)$',  # Text in parentheses
        r'^e\.g\.|^i\.e\.|^Example:',
        r'^For example',
        r'^Such as',
        r'^Note:',
        r'^\*',  # Asterisk note
    ]
    
    def __init__(self):
        self.classification_stats = {content_type: 0 for content_type in ContentType}
        
    def classify_content(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Classify a piece of text and return detailed information
        
        Returns:
            Dict with:
            - content_type: ContentType enum value
            - text: Original text
            - cleaned_text: Cleaned version for display
            - metadata: Additional information based on type
        """
        if not text or not text.strip():
            return None
            
        text = text.strip()
        
        # Check for headings first (they're usually obvious)
        if self._is_heading(text):
            return self._create_classification(ContentType.HEADING, text)
        
        # Check for legal text
        if self._is_legal_text(text):
            return self._create_classification(ContentType.LEGAL_TEXT, text)
        
        # Check for instructions
        if self._is_instruction(text):
            return self._create_classification(ContentType.INSTRUCTION, text)
        
        # Check for help text
        if self._is_help_text(text):
            return self._create_classification(ContentType.HELP_TEXT, text)
        
        # Check for fields
        field_info = self._extract_field_info(text)
        if field_info:
            return field_info
        
        # Check if it's a label for a field (ends with colon, short)
        if text.endswith(':') and len(text) < 50:
            return self._create_classification(ContentType.LABEL, text)
        
        # Default to instruction if it's descriptive text
        if len(text) > 50:
            return self._create_classification(ContentType.INSTRUCTION, text)
        
        # Short text might be a label or option
        return self._create_classification(ContentType.LABEL, text)
    
    def _is_heading(self, text: str) -> bool:
        """Check if text is a heading"""
        for pattern in self.HEADING_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_legal_text(self, text: str) -> bool:
        """Check if text is legal text"""
        for pattern in self.LEGAL_TEXT_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_instruction(self, text: str) -> bool:
        """Check if text is an instruction"""
        for pattern in self.INSTRUCTION_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_help_text(self, text: str) -> bool:
        """Check if text is help text"""
        for pattern in self.HELP_TEXT_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_field_info(self, text: str) -> Optional[Dict]:
        """Extract field information if text contains a field"""
        for pattern in self.FIELD_INDICATORS:
            if re.search(pattern, text):
                # Extract the label and field parts
                label_text = re.sub(pattern, '', text).strip()
                if label_text.endswith(':'):
                    label_text = label_text[:-1].strip()
                
                # Determine field type
                field_type = self._determine_field_type(text, label_text)
                
                classification = self._create_classification(ContentType.FIELD, text)
                classification['metadata'].update({
                    'label': label_text,
                    'field_type': field_type,
                    'required': self._is_required_field(text, label_text)
                })
                
                return classification
        
        return None
    
    def _determine_field_type(self, text: str, label: str) -> str:
        """Determine the type of field"""
        text_lower = text.lower()
        label_lower = label.lower()
        
        if any(word in label_lower for word in ['date', 'born', 'birth', 'marriage', 'separation']):
            return 'date'
        elif any(word in label_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in label_lower for word in ['phone', 'telephone', 'fax', 'mobile', 'cell']):
            return 'phone'
        elif '$' in text or any(word in label_lower for word in ['amount', 'income', 'expense', 'payment', 'cost']):
            return 'currency'
        elif any(word in label_lower for word in ['number of', 'how many', 'count']):
            return 'number'
        elif '☐' in text or '□' in text or '[ ]' in text:
            return 'checkbox'
        elif any(word in label_lower for word in ['address', 'street', 'city', 'province', 'postal']):
            return 'address'
        else:
            return 'text'
    
    def _is_required_field(self, text: str, label: str) -> bool:
        """Determine if field is required"""
        label_lower = label.lower()
        if any(word in label_lower for word in ['court file', 'name', 'applicant', 'respondent']):
            return True
        if '*' in text or '(required)' in text.lower() or '(mandatory)' in text.lower():
            return True
        return False
    
    def _create_classification(self, content_type: ContentType, text: str) -> Dict:
        """Create a classification result"""
        self.classification_stats[content_type] += 1
        
        return {
            'content_type': content_type.value,
            'text': text,
            'cleaned_text': self._clean_text(text),
            'metadata': {
                'length': len(text),
                'has_colon': text.endswith(':'),
                'is_caps': text.isupper(),
                'line_count': text.count('\n') + 1
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for display"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove field markers
        text = re.sub(r'_{2,}', '', text)
        text = re.sub(r'\[\s*\]', '', text)
        text = text.replace('☐', '').replace('□', '')
        # Trim if too long
        if len(text) > 200:
            text = text[:197] + '...'
        return text.strip()
    
    def classify_document_content(self, lines: List[str]) -> List[Dict]:
        """Classify all lines in a document"""
        results = []
        
        for i, line in enumerate(lines):
            if not line or not line.strip():
                continue
            
            # Provide context from surrounding lines
            context = {
                'line_number': i,
                'prev_line': lines[i-1] if i > 0 else None,
                'next_line': lines[i+1] if i < len(lines)-1 else None
            }
            
            classification = self.classify_content(line, context)
            if classification:
                classification['line_number'] = i
                results.append(classification)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get classification statistics"""
        return {
            'total': sum(self.classification_stats.values()),
            'by_type': {ct.value: count for ct, count in self.classification_stats.items()},
            'field_count': self.classification_stats[ContentType.FIELD],
            'instruction_count': self.classification_stats[ContentType.INSTRUCTION],
            'legal_text_count': self.classification_stats[ContentType.LEGAL_TEXT]
        }

def test_classifier():
    """Test the content classifier"""
    classifier = ContentClassifier()
    
    test_cases = [
        # Fields
        "Court File Number: _______________",
        "Applicant's Name: _______________",
        "Date of Birth: ___/___/____",
        "Monthly Income: $__________",
        "☐ I agree to the terms",
        
        # Instructions
        "Please complete all sections of this form",
        "You must provide the following information:",
        "Fill out this section if you have children",
        
        # Legal text
        "NOTE: You must file this form within 30 days",
        "Pursuant to the Family Law Act, section 33",
        "WARNING: False statements may result in penalties",
        
        # Headings
        "PART 1: IDENTIFICATION",
        "Section A: Personal Information",
        "FINANCIAL INFORMATION",
        
        # Help text
        "(Enter your full legal name)",
        "e.g., 123 Main Street",
        "Example: John Smith",
        
        # Labels
        "Your Information:",
        "Address:",
        "Phone Number:",
    ]
    
    print("Content Classification Test Results\n" + "="*50)
    
    for text in test_cases:
        result = classifier.classify_content(text)
        if result:
            print(f"\nText: {text[:50]}...")
            print(f"Type: {result['content_type']}")
            if result['content_type'] == 'field' and 'metadata' in result:
                print(f"  Label: {result['metadata'].get('label', 'N/A')}")
                print(f"  Field Type: {result['metadata'].get('field_type', 'N/A')}")
                print(f"  Required: {result['metadata'].get('required', False)}")
    
    print("\n" + "="*50)
    print("Statistics:")
    stats = classifier.get_statistics()
    print(f"Total items: {stats['total']}")
    for content_type, count in stats['by_type'].items():
        if count > 0:
            print(f"  {content_type.value}: {count}")

if __name__ == "__main__":
    test_classifier()