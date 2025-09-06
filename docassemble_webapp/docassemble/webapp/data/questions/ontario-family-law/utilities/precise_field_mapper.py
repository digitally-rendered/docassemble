#!/usr/bin/env python3
"""
Precise Field Mapper for Ontario Family Law Forms
Creates exact field mappings for data templating back into forms
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field as dataclass_field
from docx import Document
from docx.document import Document as DocumentType
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell
import hashlib


@dataclass
class PreciseField:
    """Represents a precisely mapped field in a form"""
    
    # Identification
    field_id: str  # Unique identifier
    field_key: str  # Key for data mapping
    
    # Location in document
    location_type: str  # 'paragraph', 'table', 'content_control', 'checkbox', 'textbox'
    paragraph_index: Optional[int] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    cell_index: Optional[int] = None
    content_control_id: Optional[str] = None
    
    # Field characteristics
    field_type: str = "text"  # text, area, checkbox, date, currency
    field_label: str = ""
    placeholder_text: str = ""
    
    # For text replacement
    marker_start: str = ""  # Text before the field
    marker_end: str = ""    # Text after the field
    full_context: str = ""  # Full paragraph/cell text
    
    # Validation
    max_length: Optional[int] = None
    required: bool = False
    pattern: Optional[str] = None
    
    # Metadata
    section: str = ""
    page_estimate: int = 1
    
    def get_unique_signature(self) -> str:
        """Create unique signature for this field location"""
        sig = f"{self.location_type}:{self.field_id}"
        if self.table_index is not None:
            sig += f":T{self.table_index}:R{self.row_index}:C{self.cell_index}"
        elif self.paragraph_index is not None:
            sig += f":P{self.paragraph_index}"
        return sig


class PreciseFieldMapper:
    """Maps fields precisely for bidirectional data flow"""
    
    # Patterns for different field types
    FIELD_MARKERS = {
        # Underscores indicate fill-in fields
        'underscore': r'_{3,}',  # 3+ underscores
        
        # Brackets indicate fields
        'brackets': r'\[([^\]]+)\]',  # [field_name]
        
        # Parenthetical instructions
        'instructions': r'\((?:insert|enter|specify|provide)[^)]+\)',
        
        # Colons followed by space (common in forms)
        'colon_field': r':[\s_]+(?:\n|$)',
        
        # Checkbox patterns
        'checkbox': r'☐|□|\[\s*\]|\(\s*\)',
        
        # Date patterns
        'date_field': r'(?:Date|date):?\s*_{3,}|(?:dd|mm|yyyy)',
    }
    
    # Long-form text indicators
    LONG_FORM_MARKERS = [
        r'(?:provide|give|describe|explain|state|list)\s+(?:details?|reasons?|facts?)',
        r'(?:if\s+)?(?:yes|applicable),?\s+(?:provide|explain|describe)',
        r'additional\s+information',
        r'comments?:?\s*$',
        r'details?:?\s*$',
        r'explanation:?\s*$',
        r'narrative:?\s*$',
        r'grounds?:?\s*$',
        r'circumstances?:?\s*$',
        r'history:?\s*$',
    ]
    
    def __init__(self, form_path: str):
        self.form_path = Path(form_path)
        self.doc: Optional[DocumentType] = None
        self.fields: List[PreciseField] = []
        self.field_map: Dict[str, PreciseField] = {}
        
    def map_all_fields(self) -> List[PreciseField]:
        """Map all fields in the document with precise locations"""
        
        if self.form_path.suffix.lower() == '.docx':
            return self._map_docx_fields()
        elif self.form_path.suffix.lower() == '.pdf':
            return self._map_pdf_fields()
        else:
            raise ValueError(f"Unsupported file type: {self.form_path.suffix}")
    
    def _map_docx_fields(self) -> List[PreciseField]:
        """Map fields in DOCX documents"""
        
        self.doc = Document(self.form_path)
        self.fields = []
        
        # 1. Map content controls (best for templating)
        self._map_content_controls()
        
        # 2. Map form fields in paragraphs
        self._map_paragraph_fields()
        
        # 3. Map fields in tables
        self._map_table_fields()
        
        # 4. Map checkboxes
        self._map_checkboxes()
        
        # 5. Map long-form text areas
        self._map_long_form_areas()
        
        # Build field map for quick lookup
        self._build_field_map()
        
        return self.fields
    
    def _map_content_controls(self):
        """Map Word content controls (structured document tags)"""
        
        # This requires parsing the underlying XML
        try:
            for element in self.doc.element.xpath('//w:sdt'):
                # Extract properties
                props = element.find('.//w:sdtPr', namespaces=element.nsmap)
                if props is not None:
                    # Get tag/title
                    tag_elem = props.find('.//w:tag', namespaces=element.nsmap)
                    title_elem = props.find('.//w:alias', namespaces=element.nsmap)
                    
                    tag = tag_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if tag_elem is not None else ''
                    title = title_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if title_elem is not None else ''
                    
                    if tag or title:
                        field = PreciseField(
                            field_id=f"cc_{tag or title}",
                            field_key=self._normalize_field_key(tag or title),
                            location_type='content_control',
                            content_control_id=tag or title,
                            field_label=title or tag
                        )
                        self.fields.append(field)
                        
        except Exception as e:
            print(f"Note: Could not parse content controls: {e}")
    
    def _map_paragraph_fields(self):
        """Map fields in regular paragraphs"""
        
        for p_idx, paragraph in enumerate(self.doc.paragraphs):
            text = paragraph.text.strip()
            
            if not text:
                continue
            
            # Look for underscore fields
            underscore_matches = list(re.finditer(self.FIELD_MARKERS['underscore'], text))
            
            for match in underscore_matches:
                # Get context around the field
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Extract label (text before underscores)
                before_text = text[:match.start()].strip()
                label = self._extract_field_label(before_text)
                
                field = PreciseField(
                    field_id=f"p{p_idx}_pos{match.start()}",
                    field_key=self._normalize_field_key(label),
                    location_type='paragraph',
                    paragraph_index=p_idx,
                    field_label=label,
                    marker_start=text[max(0, match.start()-20):match.start()],
                    marker_end=text[match.end():min(len(text), match.end()+20)],
                    full_context=context,
                    field_type=self._determine_field_type(label, context)
                )
                self.fields.append(field)
            
            # Look for bracketed fields
            bracket_matches = list(re.finditer(self.FIELD_MARKERS['brackets'], text))
            
            for match in bracket_matches:
                field_name = match.group(1)
                
                field = PreciseField(
                    field_id=f"p{p_idx}_bracket_{match.start()}",
                    field_key=self._normalize_field_key(field_name),
                    location_type='paragraph',
                    paragraph_index=p_idx,
                    field_label=field_name,
                    placeholder_text=field_name,
                    marker_start=text[max(0, match.start()-20):match.start()],
                    marker_end=text[match.end():min(len(text), match.end()+20)],
                    full_context=text
                )
                self.fields.append(field)
    
    def _map_table_fields(self):
        """Map fields within tables"""
        
        for t_idx, table in enumerate(self.doc.tables):
            for r_idx, row in enumerate(table.rows):
                for c_idx, cell in enumerate(row.cells):
                    text = cell.text.strip()
                    
                    if not text:
                        continue
                    
                    # Check for field markers
                    has_underscore = re.search(self.FIELD_MARKERS['underscore'], text)
                    has_bracket = re.search(self.FIELD_MARKERS['brackets'], text)
                    has_colon = re.search(self.FIELD_MARKERS['colon_field'], text)
                    
                    if has_underscore or has_bracket or has_colon:
                        # This cell contains a field
                        label = self._extract_field_label_from_cell(table, r_idx, c_idx)
                        
                        field = PreciseField(
                            field_id=f"t{t_idx}_r{r_idx}_c{c_idx}",
                            field_key=self._normalize_field_key(label),
                            location_type='table',
                            table_index=t_idx,
                            row_index=r_idx,
                            cell_index=c_idx,
                            field_label=label,
                            full_context=text,
                            field_type=self._determine_field_type(label, text)
                        )
                        self.fields.append(field)
    
    def _map_checkboxes(self):
        """Map checkbox fields"""
        
        checkbox_pattern = re.compile(self.FIELD_MARKERS['checkbox'])
        
        for p_idx, paragraph in enumerate(self.doc.paragraphs):
            text = paragraph.text
            
            matches = list(checkbox_pattern.finditer(text))
            
            for match in matches:
                # Get label (text after checkbox)
                after_text = text[match.end():].strip()
                label = after_text.split('\n')[0] if after_text else ""
                
                field = PreciseField(
                    field_id=f"cb_p{p_idx}_{match.start()}",
                    field_key=self._normalize_field_key(label),
                    location_type='checkbox',
                    paragraph_index=p_idx,
                    field_label=label,
                    field_type='checkbox',
                    marker_start=text[max(0, match.start()-10):match.start()],
                    marker_end=text[match.end():min(len(text), match.end()+50)]
                )
                self.fields.append(field)
    
    def _map_long_form_areas(self):
        """Map long-form text areas"""
        
        for p_idx, paragraph in enumerate(self.doc.paragraphs):
            text = paragraph.text.lower().strip()
            
            for pattern in self.LONG_FORM_MARKERS:
                if re.search(pattern, text):
                    # Check if followed by space for writing
                    if self._has_writing_space_after(p_idx):
                        field = PreciseField(
                            field_id=f"lf_p{p_idx}",
                            field_key=self._normalize_field_key(paragraph.text),
                            location_type='paragraph',
                            paragraph_index=p_idx,
                            field_label=paragraph.text.strip(),
                            field_type='area',
                            required=True  # Long-form usually required
                        )
                        self.fields.append(field)
                    break
    
    def _extract_field_label(self, text: str) -> str:
        """Extract field label from text before field marker"""
        
        # Remove common prefixes
        text = re.sub(r'^\d+\.?\s*', '', text)  # Remove numbering
        
        # Take last meaningful part
        parts = text.split(':')
        if parts:
            label = parts[-1].strip()
        else:
            label = text.strip()
        
        # Clean up
        label = re.sub(r'[_\s]+$', '', label)  # Remove trailing underscores/spaces
        
        return label[:100]  # Limit length
    
    def _extract_field_label_from_cell(self, table: Table, row_idx: int, cell_idx: int) -> str:
        """Extract label from table cell or neighboring cells"""
        
        row = table.rows[row_idx]
        cell = row.cells[cell_idx]
        
        # Check current cell
        text = cell.text.strip()
        if ':' in text:
            return text.split(':')[0].strip()
        
        # Check cell to the left (label column)
        if cell_idx > 0:
            left_cell = row.cells[cell_idx - 1]
            left_text = left_cell.text.strip()
            if left_text and not re.search(self.FIELD_MARKERS['underscore'], left_text):
                return left_text
        
        # Check cell above (header row)
        if row_idx > 0:
            header_cell = table.rows[0].cells[cell_idx]
            header_text = header_cell.text.strip()
            if header_text:
                return header_text
        
        return f"Field_{row_idx}_{cell_idx}"
    
    def _determine_field_type(self, label: str, context: str) -> str:
        """Determine field type from label and context"""
        
        label_lower = label.lower()
        context_lower = context.lower()
        
        if any(word in label_lower for word in ['date', 'when', 'birthday', 'born']):
            return 'date'
        elif any(word in label_lower for word in ['$', 'amount', 'income', 'expense', 'cost', 'value']):
            return 'currency'
        elif any(word in label_lower for word in ['email', 'e-mail']):
            return 'email'
        elif any(word in label_lower for word in ['phone', 'telephone', 'mobile', 'fax']):
            return 'phone'
        elif any(word in label_lower for word in ['postal', 'zip']):
            return 'postal_code'
        elif any(word in label_lower for word in ['describe', 'explain', 'details', 'narrative']):
            return 'area'
        else:
            return 'text'
    
    def _normalize_field_key(self, text: str) -> str:
        """Create normalized field key for data mapping"""
        
        # Remove special characters
        key = re.sub(r'[^a-zA-Z0-9\s_]', '', text)
        
        # Convert to snake_case
        key = re.sub(r'\s+', '_', key.strip())
        key = key.lower()
        
        # Remove duplicate underscores
        key = re.sub(r'_+', '_', key)
        
        # Limit length
        return key[:50]
    
    def _has_writing_space_after(self, paragraph_index: int) -> bool:
        """Check if there's writing space after a paragraph"""
        
        # Check next few paragraphs
        for i in range(paragraph_index + 1, min(paragraph_index + 5, len(self.doc.paragraphs))):
            text = self.doc.paragraphs[i].text.strip()
            
            # Empty paragraphs or lines suggest writing space
            if not text or text == '_' * len(text):
                return True
        
        return False
    
    def _build_field_map(self):
        """Build quick lookup map"""
        
        self.field_map = {}
        for field in self.fields:
            # Multiple keys for same field
            self.field_map[field.field_id] = field
            self.field_map[field.field_key] = field
            self.field_map[field.get_unique_signature()] = field
    
    def template_data(self, data: Dict[str, Any], output_path: str = None) -> bool:
        """Template data back into the form"""
        
        if not self.doc:
            self.doc = Document(self.form_path)
        
        if not self.fields:
            self.map_all_fields()
        
        # Template each field
        for field_key, value in data.items():
            field = self.field_map.get(field_key)
            
            if not field:
                # Try normalized key
                normalized_key = self._normalize_field_key(field_key)
                field = self.field_map.get(normalized_key)
            
            if field:
                self._template_field(field, value)
        
        # Save
        if output_path:
            self.doc.save(output_path)
            return True
        
        return False
    
    def _template_field(self, field: PreciseField, value: Any):
        """Template a single field value"""
        
        if field.location_type == 'paragraph':
            paragraph = self.doc.paragraphs[field.paragraph_index]
            
            # Replace underscores or brackets with value
            if field.marker_start and field.marker_end:
                old_text = paragraph.text
                # Find and replace the field marker
                new_text = old_text.replace(
                    field.marker_start + ('_' * 10) + field.marker_end,
                    field.marker_start + str(value) + field.marker_end
                )
                paragraph.text = new_text
            
        elif field.location_type == 'table':
            table = self.doc.tables[field.table_index]
            cell = table.rows[field.row_index].cells[field.cell_index]
            
            # Replace field marker with value
            old_text = cell.text
            # Simple replacement for now
            if '_' * 3 in old_text:
                cell.text = old_text.replace('_' * 10, str(value))
            else:
                cell.text = str(value)
        
        elif field.location_type == 'checkbox':
            if value:
                # Check the checkbox (replace empty with X)
                paragraph = self.doc.paragraphs[field.paragraph_index]
                paragraph.text = paragraph.text.replace('☐', '☒').replace('□', '■').replace('[ ]', '[X]')
    
    def export_field_map(self, output_path: str = None) -> Dict:
        """Export field map for external use"""
        
        if not self.fields:
            self.map_all_fields()
        
        export_data = {
            'form_path': str(self.form_path),
            'total_fields': len(self.fields),
            'field_types': {},
            'fields': []
        }
        
        # Count field types
        for field in self.fields:
            field_type = field.field_type
            export_data['field_types'][field_type] = export_data['field_types'].get(field_type, 0) + 1
        
        # Export field details
        for field in self.fields:
            export_data['fields'].append({
                'id': field.field_id,
                'key': field.field_key,
                'label': field.field_label,
                'type': field.field_type,
                'location': field.location_type,
                'signature': field.get_unique_signature(),
                'required': field.required,
                'section': field.section,
                'context': field.full_context[:100] if field.full_context else ""
            })
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        return export_data


def analyze_form_for_templating(form_path: str):
    """Analyze a form and create precise field mapping"""
    
    mapper = PreciseFieldMapper(form_path)
    fields = mapper.map_all_fields()
    
    print(f"\n📋 Form: {Path(form_path).name}")
    print(f"📍 Total fields mapped: {len(fields)}")
    
    # Group by type
    by_type = {}
    for field in fields:
        by_type.setdefault(field.field_type, []).append(field)
    
    print("\n📊 Field Types:")
    for field_type, type_fields in by_type.items():
        print(f"  - {field_type}: {len(type_fields)} fields")
    
    # Group by location
    by_location = {}
    for field in fields:
        by_location.setdefault(field.location_type, []).append(field)
    
    print("\n📍 Field Locations:")
    for location, loc_fields in by_location.items():
        print(f"  - {location}: {len(loc_fields)} fields")
    
    # Export map
    output_file = Path(form_path).stem + "_field_map.json"
    export_data = mapper.export_field_map(output_file)
    
    print(f"\n✅ Field map exported to: {output_file}")
    
    return mapper


def test_templating(form_path: str, test_data: Dict[str, Any]):
    """Test templating data back into form"""
    
    mapper = PreciseFieldMapper(form_path)
    mapper.map_all_fields()
    
    # Create output path
    output_path = Path(form_path).stem + "_filled.docx"
    
    # Template the data
    success = mapper.template_data(test_data, output_path)
    
    if success:
        print(f"✅ Templated form saved to: {output_path}")
    else:
        print("❌ Templating failed")
    
    return success


if __name__ == "__main__":
    # Test on Form 8
    form_path = "workflow_output/ontario_forms/form_8_-_application_general_flr-8-jun25-en.docx"
    
    if Path(form_path).exists():
        # Analyze the form
        mapper = analyze_form_for_templating(form_path)
        
        # Test templating with sample data
        test_data = {
            "applicant_name": "John Smith",
            "respondent_name": "Jane Doe",
            "court_file_number": "FC-24-12345",
            "date": "2024-01-15",
            "grounds": "This is a test of long-form text field templating."
        }
        
        test_templating(form_path, test_data)
    else:
        print(f"Form not found at: {form_path}")