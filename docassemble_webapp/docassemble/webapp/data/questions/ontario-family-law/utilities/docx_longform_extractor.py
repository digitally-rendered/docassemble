#!/usr/bin/env python3
"""
DOCX Long-Form Field Extractor for Ontario Family Law Forms
Specifically designed to extract narrative text areas from DOCX forms
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from docx import Document
from dataclasses import dataclass, asdict


@dataclass
class LongFormDocxField:
    """Represents a long-form field in a DOCX document"""
    field_id: str
    field_key: str
    prompt: str
    instructions: str
    table_location: Optional[Dict] = None  # {table: X, row: Y, cell: Z}
    field_type: str = "area"  # Default to textarea for long-form
    required: bool = False
    min_lines: int = 3
    max_chars: Optional[int] = None
    section: str = ""
    category: str = ""  # divorce, support, property, etc.
    

class DocxLongFormExtractor:
    """Extract long-form narrative fields from DOCX forms"""
    
    # Key phrases that indicate long-form fields
    LONG_FORM_INDICATORS = {
        'instructions': [
            r'give\s+details',
            r'provide\s+details',
            r'explain',
            r'describe',
            r'list\s+(?:all\s+)?',
            r'state\s+(?:the\s+)?',
            r'set\s+out',
            r'specify',
            r'outline',
            r'include\s+any',
        ],
        'legal_terms': [
            r'grounds?\s+(?:for|of)',
            r'facts?\s+(?:supporting|that)',
            r'legal\s+basis',
            r'circumstances?',
            r'reasons?\s+(?:for|why)',
            r'claim(?:s)?\s+(?:for|relating)',
            r'history\s+(?:of)?',
            r'evidence\s+(?:of)?',
            r'allegations?',
        ],
        'form_specific': [
            r'important\s+facts',
            r'other\s+claim',
            r'additional\s+(?:information|page)',
            r'attach\s+(?:an?\s+)?(?:additional|separate)',
            r'continue\s+on',
            r'if\s+you\s+need\s+more\s+space',
        ]
    }
    
    # Section categorization
    SECTION_CATEGORIES = {
        'divorce': ['divorce', 'separation', 'marriage', 'adultery', 'cruelty', 'breakdown'],
        'children': ['child', 'custody', 'access', 'parenting', 'decision-making'],
        'support': ['support', 'maintenance', 'income', 'expense'],
        'property': ['property', 'asset', 'debt', 'matrimonial', 'equalization'],
        'enforcement': ['enforcement', 'garnishment', 'seizure'],
        'other': ['other', 'additional', 'general']
    }
    
    def __init__(self, docx_path: str):
        self.docx_path = Path(docx_path)
        self.doc = Document(docx_path)
        self.form_number = self._extract_form_number()
        self.fields = []
        
    def _extract_form_number(self) -> str:
        """Extract form number from filename"""
        filename = self.docx_path.stem.lower()
        match = re.search(r'form[_\s-]?(\d+[a-z]?)', filename)
        if match:
            return match.group(1).upper()
        return "unknown"
    
    def extract_all_longform_fields(self) -> List[LongFormDocxField]:
        """Main extraction method"""
        self.fields = []
        
        # Scan all tables for long-form prompts
        for t_idx, table in enumerate(self.doc.tables):
            self._extract_from_table(table, t_idx)
        
        # Also check paragraphs (rare but possible)
        for p_idx, paragraph in enumerate(self.doc.paragraphs):
            self._extract_from_paragraph(paragraph, p_idx)
        
        # Deduplicate and clean
        self.fields = self._deduplicate_fields(self.fields)
        
        return self.fields
    
    def _extract_from_table(self, table, table_idx: int):
        """Extract long-form fields from a table"""
        
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                text = cell.text.strip()
                
                if not text or len(text) < 20:
                    continue
                
                # Check if this is a long-form prompt
                if self._is_longform_prompt(text):
                    # Check if there's space for writing
                    has_space = self._check_for_writing_space(table, r_idx, c_idx)
                    
                    field = self._create_field_from_text(
                        text=text,
                        location={
                            'table': table_idx,
                            'row': r_idx,
                            'cell': c_idx
                        },
                        has_writing_space=has_space
                    )
                    
                    if field:
                        self.fields.append(field)
    
    def _extract_from_paragraph(self, paragraph, p_idx: int):
        """Extract long-form fields from paragraphs"""
        
        text = paragraph.text.strip()
        
        if text and self._is_longform_prompt(text):
            field = self._create_field_from_text(
                text=text,
                location={'paragraph': p_idx},
                has_writing_space=True  # Assume paragraphs with prompts have space
            )
            
            if field:
                self.fields.append(field)
    
    def _is_longform_prompt(self, text: str) -> bool:
        """Check if text contains long-form field indicators"""
        
        text_lower = text.lower()
        
        # Check for any indicator patterns
        for category, patterns in self.LONG_FORM_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return True
        
        return False
    
    def _check_for_writing_space(self, table, row_idx: int, cell_idx: int) -> bool:
        """Check if there's space for writing after this cell"""
        
        # Check if next rows are empty or have lines
        if row_idx < len(table.rows) - 1:
            next_row = table.rows[row_idx + 1]
            if cell_idx < len(next_row.cells):
                next_cell_text = next_row.cells[cell_idx].text.strip()
                
                # Empty or just lines/dots suggests writing space
                if not next_cell_text or all(c in '._─' for c in next_cell_text):
                    return True
        
        # Check if cell spans multiple rows (merged cells often indicate space)
        # This is complex in python-docx, so we use a heuristic
        cell_text_lines = table.rows[row_idx].cells[cell_idx].text.count('\n')
        if cell_text_lines > 3:
            return True
        
        return False
    
    def _create_field_from_text(self, text: str, location: Dict, has_writing_space: bool) -> Optional[LongFormDocxField]:
        """Create a field object from prompt text"""
        
        # Extract the actual prompt
        prompt = self._clean_prompt(text)
        
        # Extract instructions if present
        instructions = self._extract_instructions(text)
        
        # Determine category
        category = self._categorize_field(text)
        
        # Generate field ID and key
        field_id = self._generate_field_id(location, prompt)
        field_key = self._generate_field_key(prompt, category)
        
        # Determine if required
        required = self._is_required(text)
        
        # Estimate size needed
        min_lines = self._estimate_lines_needed(text, has_writing_space)
        
        return LongFormDocxField(
            field_id=field_id,
            field_key=field_key,
            prompt=prompt,
            instructions=instructions,
            table_location=location if 'table' in location else None,
            field_type="area",
            required=required,
            min_lines=min_lines,
            section=self._determine_section(text),
            category=category
        )
    
    def _clean_prompt(self, text: str) -> str:
        """Clean and extract the main prompt from text"""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Extract first sentence or up to first parenthetical
        match = re.match(r'^([^.!?(]+(?:[.!?]|$))', text)
        if match:
            prompt = match.group(1).strip()
        else:
            prompt = text[:200].strip()
        
        return prompt
    
    def _extract_instructions(self, text: str) -> str:
        """Extract parenthetical instructions"""
        
        # Look for text in parentheses
        match = re.search(r'\(([^)]+)\)', text)
        if match:
            return match.group(1)
        
        # Look for text after "Include" or "Provide"
        match = re.search(r'(?:Include|Provide|Give)([^.]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _categorize_field(self, text: str) -> str:
        """Categorize field based on content"""
        
        text_lower = text.lower()
        
        for category, keywords in self.SECTION_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "other"
    
    def _generate_field_id(self, location: Dict, prompt: str) -> str:
        """Generate unique field ID"""
        
        if 'table' in location:
            return f"form{self.form_number}_t{location['table']}_r{location['row']}_c{location['cell']}"
        elif 'paragraph' in location:
            return f"form{self.form_number}_p{location['paragraph']}"
        else:
            # Hash the prompt for uniqueness
            import hashlib
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            return f"form{self.form_number}_{prompt_hash}"
    
    def _generate_field_key(self, prompt: str, category: str) -> str:
        """Generate field key for data mapping"""
        
        # Create snake_case key from prompt
        key = re.sub(r'[^\w\s]', '', prompt.lower())
        key = re.sub(r'\s+', '_', key)
        key = key[:40]  # Limit length
        
        return f"form{self.form_number}_{category}_{key}"
    
    def _is_required(self, text: str) -> bool:
        """Determine if field is required"""
        
        required_indicators = ['must', 'required', 'mandatory', 'important facts']
        text_lower = text.lower()
        
        return any(indicator in text_lower for indicator in required_indicators)
    
    def _estimate_lines_needed(self, text: str, has_writing_space: bool) -> int:
        """Estimate minimum lines needed for response"""
        
        # Base estimate on prompt type
        if 'detail' in text.lower() or 'explain' in text.lower():
            return 5
        elif 'list' in text.lower():
            return 10
        elif 'facts' in text.lower() or 'circumstances' in text.lower():
            return 8
        elif has_writing_space:
            return 5
        else:
            return 3
    
    def _determine_section(self, text: str) -> str:
        """Determine form section from text"""
        
        text_lower = text.lower()
        
        if 'divorce' in text_lower:
            return "Divorce Claims"
        elif 'support' in text_lower:
            return "Support Claims"
        elif 'property' in text_lower:
            return "Property Claims"
        elif 'child' in text_lower:
            return "Children"
        elif 'fact' in text_lower:
            return "Supporting Facts"
        else:
            return "Other Claims"
    
    def _deduplicate_fields(self, fields: List[LongFormDocxField]) -> List[LongFormDocxField]:
        """Remove duplicate fields (from merged cells)"""
        
        seen_prompts = set()
        unique_fields = []
        
        for field in fields:
            # Create signature for deduplication
            signature = field.prompt[:50]
            
            if signature not in seen_prompts:
                seen_prompts.add(signature)
                unique_fields.append(field)
        
        return unique_fields
    
    def export_to_json(self, output_path: str = None) -> Dict:
        """Export fields to JSON format"""
        
        if not self.fields:
            self.extract_all_longform_fields()
        
        export_data = {
            'form_number': self.form_number,
            'form_file': str(self.docx_path),
            'total_longform_fields': len(self.fields),
            'categories': {},
            'fields': []
        }
        
        # Count by category
        for field in self.fields:
            cat = field.category
            export_data['categories'][cat] = export_data['categories'].get(cat, 0) + 1
        
        # Export fields
        for field in self.fields:
            export_data['fields'].append(asdict(field))
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        return export_data


def process_all_forms():
    """Process all Ontario forms for long-form fields"""
    
    forms_dir = Path("workflow_output/ontario_forms")
    
    if not forms_dir.exists():
        print("Forms directory not found")
        return
    
    # Priority forms
    priority_forms = ["8", "8A", "10", "36", "17A", "17C", "13A"]
    
    all_results = {}
    
    for form_num in priority_forms:
        # Find DOCX file
        pattern = f"*form_{form_num}_*.docx"
        matches = list(forms_dir.glob(pattern))
        
        if not matches:
            pattern = f"*form_{form_num.lower()}_*.docx"
            matches = list(forms_dir.glob(pattern))
        
        if matches:
            docx_file = matches[0]
            print(f"\n📄 Processing Form {form_num}: {docx_file.name}")
            
            extractor = DocxLongFormExtractor(str(docx_file))
            fields = extractor.extract_all_longform_fields()
            
            print(f"  ✅ Found {len(fields)} long-form fields")
            
            if fields:
                print("  📝 Fields:")
                for field in fields[:3]:  # Show first 3
                    print(f"     - {field.prompt[:60]}...")
                    if field.instructions:
                        print(f"       Instructions: {field.instructions[:50]}...")
            
            # Export
            output_file = f"parsed_forms/form_{form_num}_longform_fields.json"
            export_data = extractor.export_to_json(output_file)
            all_results[form_num] = export_data
    
    # Save combined results
    with open("all_longform_fields.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n📊 Summary:")
    for form_num, data in all_results.items():
        total = data['total_longform_fields']
        cats = data['categories']
        print(f"  Form {form_num}: {total} fields - {cats}")


if __name__ == "__main__":
    process_all_forms()