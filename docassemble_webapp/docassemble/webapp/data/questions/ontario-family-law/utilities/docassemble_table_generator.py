#!/usr/bin/env python3
"""
Docassemble Table and Screen Generator
Handles row/column data and groups fields into logical interview screens
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TableStructure:
    """Represents a table in the form"""
    table_id: str
    table_name: str
    table_type: str  # 'income', 'expense', 'asset', 'debt', 'children', 'custom'
    columns: List[Dict[str, Any]] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    is_repeating: bool = True  # Can add/remove rows
    page_number: int = 0
    context: str = ""
    
    # Docassemble configuration
    da_object_type: str = "DAList"
    da_variable_name: str = ""
    da_element_type: str = "DAObject"

@dataclass
class ScreenGroup:
    """Represents a logical screen/question in docassemble"""
    screen_id: str
    title: str
    subtitle: Optional[str] = None
    fields: List[Dict] = field(default_factory=list)
    tables: List[TableStructure] = field(default_factory=list)
    page_number: int = 0
    question_type: str = "fields"  # 'fields', 'table', 'review', 'signature'
    mandatory: bool = False
    depends_on: Optional[str] = None  # Conditional logic

class TableDetector:
    """
    Detects and structures tabular data from parsed fields
    """
    
    def __init__(self):
        # Patterns that indicate table structures
        self.table_indicators = {
            'income': ['income', 'earnings', 'salary', 'wages', 'benefits'],
            'expense': ['expense', 'cost', 'payment', 'spending', 'bills'],
            'asset': ['asset', 'property', 'investment', 'savings', 'account'],
            'debt': ['debt', 'loan', 'mortgage', 'credit', 'liability'],
            'children': ['child', 'children', 'dependent', 'minor'],
            'deductions': ['deduction', 'tax', 'cpp', 'ei', 'union'],
            'support': ['support', 'alimony', 'maintenance', 'payment']
        }
        
        # Column patterns for common tables
        self.column_patterns = {
            'financial': ['description', 'amount', 'frequency', 'annual'],
            'children': ['name', 'birthdate', 'age', 'school', 'residence'],
            'property': ['description', 'value', 'debt', 'net_value'],
            'support': ['payor', 'recipient', 'amount', 'frequency', 'start_date']
        }
    
    def detect_tables(self, validated_fields: List) -> List[TableStructure]:
        """
        Detect table structures from validated fields
        """
        logger.info("Detecting table structures from fields...")
        
        tables = []
        field_groups = self._group_fields_by_context(validated_fields)
        
        for context_key, fields in field_groups.items():
            # Check if this looks like a table
            if self._is_table_structure(fields):
                table = self._create_table_structure(fields, context_key)
                if table:
                    tables.append(table)
        
        # Also detect implicit tables from repeating patterns
        implicit_tables = self._detect_implicit_tables(validated_fields)
        tables.extend(implicit_tables)
        
        logger.info(f"Detected {len(tables)} table structures")
        return tables
    
    def _group_fields_by_context(self, fields: List) -> Dict[str, List]:
        """
        Group fields by their context (table, row, etc.)
        """
        groups = defaultdict(list)
        
        for field_obj in fields:
            # Check for table context
            context = getattr(field_obj, 'context', '')
            
            # Look for table indicators
            if 'table' in context.lower():
                # Extract table identifier
                table_match = re.search(r'table[_\s]+(\d+|\w+)', context.lower())
                if table_match:
                    table_key = f"table_{table_match.group(1)}"
                    groups[table_key].append(field_obj)
            
            # Look for row/column patterns
            elif re.search(r'row[_\s]+\d+|column[_\s]+\d+', context.lower()):
                groups['implicit_table'].append(field_obj)
            
            # Group by label patterns (e.g., numbered items)
            elif self._has_row_pattern(field_obj):
                groups['numbered_items'].append(field_obj)
        
        return groups
    
    def _is_table_structure(self, fields: List) -> bool:
        """
        Check if fields represent a table structure
        """
        if len(fields) < 2:
            return False
        
        # Check for row/column mentions
        has_rows = any('row' in str(getattr(f, 'context', '')).lower() for f in fields)
        has_columns = any('column' in str(getattr(f, 'context', '')).lower() for f in fields)
        
        # Check for repeating patterns
        field_types = [getattr(f, 'field_type', '') for f in fields]
        type_counts = defaultdict(int)
        for ftype in field_types:
            type_counts[ftype] += 1
        
        # If we have multiple fields of the same type, might be a table
        has_repeating = any(count > 2 for count in type_counts.values())
        
        return has_rows or has_columns or has_repeating
    
    def _create_table_structure(self, fields: List, context_key: str) -> Optional[TableStructure]:
        """
        Create a table structure from grouped fields
        """
        if not fields:
            return None
        
        # Determine table type
        table_type = self._determine_table_type(fields)
        
        # Extract columns and rows
        columns = self._extract_columns(fields)
        rows = self._extract_rows(fields)
        
        # Create table structure
        table = TableStructure(
            table_id=f"table_{context_key}",
            table_name=self._generate_table_name(table_type, fields),
            table_type=table_type,
            columns=columns,
            rows=rows,
            page_number=getattr(fields[0], 'page_number', 0),
            context=context_key
        )
        
        # Set docassemble configuration
        table.da_variable_name = self._generate_da_variable_name(table_type)
        table.da_element_type = self._get_da_element_type(table_type)
        
        return table
    
    def _determine_table_type(self, fields: List) -> str:
        """
        Determine the type of table based on field content
        """
        # Collect all text from fields
        all_text = " ".join([
            str(getattr(f, 'field_label', '')) + 
            str(getattr(f, 'canonical_name', ''))
            for f in fields
        ]).lower()
        
        # Check against table indicators
        for table_type, indicators in self.table_indicators.items():
            if any(indicator in all_text for indicator in indicators):
                return table_type
        
        return 'custom'
    
    def _extract_columns(self, fields: List) -> List[Dict]:
        """
        Extract column definitions from fields
        """
        columns = []
        seen_columns = set()
        
        for field_obj in fields:
            # Try to extract column info from context
            context = str(getattr(field_obj, 'context', ''))
            col_match = re.search(r'column[_\s]+(\d+)', context.lower())
            
            if col_match:
                col_num = int(col_match.group(1))
                col_name = getattr(field_obj, 'canonical_name', f'column_{col_num}')
                
                if col_name not in seen_columns:
                    columns.append({
                        'name': col_name,
                        'label': getattr(field_obj, 'field_label', col_name),
                        'type': getattr(field_obj, 'field_type', 'text'),
                        'required': getattr(field_obj, 'required', False),
                        'column_number': col_num
                    })
                    seen_columns.add(col_name)
        
        # If no explicit columns, infer from field patterns
        if not columns:
            columns = self._infer_columns(fields)
        
        return sorted(columns, key=lambda x: x.get('column_number', 0))
    
    def _extract_rows(self, fields: List) -> List[Dict]:
        """
        Extract row data from fields
        """
        rows = defaultdict(dict)
        
        for field_obj in fields:
            context = str(getattr(field_obj, 'context', ''))
            
            # Look for row indicators
            row_match = re.search(r'row[_\s]+(\d+)', context.lower())
            if row_match:
                row_num = int(row_match.group(1))
                col_name = getattr(field_obj, 'canonical_name', 'value')
                rows[row_num][col_name] = {
                    'value': getattr(field_obj, 'value', None),
                    'type': getattr(field_obj, 'field_type', 'text')
                }
        
        # Convert to list
        return [{'row_number': k, 'data': v} for k, v in sorted(rows.items())]
    
    def _infer_columns(self, fields: List) -> List[Dict]:
        """
        Infer column structure from field patterns
        """
        columns = []
        
        # Group by field type patterns
        type_groups = defaultdict(list)
        for field_obj in fields:
            ftype = getattr(field_obj, 'field_type', 'text')
            type_groups[ftype].append(field_obj)
        
        # Common column patterns
        if 'currency' in type_groups and 'text' in type_groups:
            # Likely a description + amount table
            columns.append({
                'name': 'description',
                'label': 'Description',
                'type': 'text',
                'required': True,
                'column_number': 1
            })
            columns.append({
                'name': 'amount',
                'label': 'Amount',
                'type': 'currency',
                'required': True,
                'column_number': 2
            })
        
        elif 'date' in type_groups and 'text' in type_groups:
            # Likely a date-based table
            columns.append({
                'name': 'item',
                'label': 'Item',
                'type': 'text',
                'required': True,
                'column_number': 1
            })
            columns.append({
                'name': 'date',
                'label': 'Date',
                'type': 'date',
                'required': False,
                'column_number': 2
            })
        
        # Default columns if nothing specific detected
        if not columns:
            for i, (ftype, fields_list) in enumerate(type_groups.items(), 1):
                columns.append({
                    'name': f'column_{i}',
                    'label': f'Column {i}',
                    'type': ftype,
                    'required': False,
                    'column_number': i
                })
        
        return columns
    
    def _detect_implicit_tables(self, fields: List) -> List[TableStructure]:
        """
        Detect tables from repeating field patterns
        """
        tables = []
        
        # Look for numbered sequences (e.g., "1. Income from employment", "2. Investment income")
        numbered_groups = defaultdict(list)
        
        for field_obj in fields:
            label = str(getattr(field_obj, 'field_label', ''))
            
            # Check for numbered patterns
            number_match = re.match(r'^(\d+)[\.\)]\s*(.+)', label)
            if number_match:
                group_key = getattr(field_obj, 'field_type', 'text')
                numbered_groups[group_key].append(field_obj)
        
        # Create tables from numbered groups
        for group_key, group_fields in numbered_groups.items():
            if len(group_fields) >= 3:  # Need at least 3 items to be a table
                table = self._create_implicit_table(group_fields, group_key)
                if table:
                    tables.append(table)
        
        return tables
    
    def _create_implicit_table(self, fields: List, group_key: str) -> Optional[TableStructure]:
        """
        Create table from implicit repeating structure
        """
        # Determine table type
        table_type = self._determine_table_type(fields)
        
        # Create columns based on field type
        columns = [
            {
                'name': 'item',
                'label': 'Item',
                'type': 'text',
                'required': True,
                'column_number': 1
            }
        ]
        
        if group_key == 'currency':
            columns.append({
                'name': 'amount',
                'label': 'Amount',
                'type': 'currency',
                'required': True,
                'column_number': 2
            })
        
        # Create rows from fields
        rows = []
        for i, field_obj in enumerate(fields, 1):
            label = str(getattr(field_obj, 'field_label', ''))
            # Remove numbering
            label_clean = re.sub(r'^\d+[\.\)]\s*', '', label)
            
            row_data = {'item': label_clean}
            if group_key == 'currency':
                row_data['amount'] = getattr(field_obj, 'value', None)
            
            rows.append({
                'row_number': i,
                'data': row_data
            })
        
        table = TableStructure(
            table_id=f"implicit_table_{table_type}",
            table_name=f"{table_type.title()} Table",
            table_type=table_type,
            columns=columns,
            rows=rows,
            page_number=getattr(fields[0], 'page_number', 0),
            context=f"Implicit {table_type} table"
        )
        
        table.da_variable_name = f"{table_type}_list"
        table.da_element_type = "DAObject"
        
        return table
    
    def _has_row_pattern(self, field_obj) -> bool:
        """
        Check if field has a row/list pattern
        """
        label = str(getattr(field_obj, 'field_label', ''))
        
        # Check for numbering
        if re.match(r'^\d+[\.\)]\s*', label):
            return True
        
        # Check for bullet points
        if re.match(r'^[•·▪▫◦‣⁃]\s*', label):
            return True
        
        # Check for letters
        if re.match(r'^[a-z][\.\)]\s*', label, re.IGNORECASE):
            return True
        
        return False
    
    def _generate_table_name(self, table_type: str, fields: List) -> str:
        """
        Generate a descriptive table name
        """
        if table_type == 'income':
            return "Sources of Income"
        elif table_type == 'expense':
            return "Monthly Expenses"
        elif table_type == 'asset':
            return "Assets"
        elif table_type == 'debt':
            return "Debts and Liabilities"
        elif table_type == 'children':
            return "Children Information"
        elif table_type == 'support':
            return "Support Payments"
        else:
            # Try to extract from field labels
            labels = [str(getattr(f, 'field_label', ''))[:20] for f in fields[:3]]
            if labels:
                return f"Table: {labels[0]}..."
            return "Custom Table"
    
    def _generate_da_variable_name(self, table_type: str) -> str:
        """
        Generate docassemble variable name for table
        """
        variable_names = {
            'income': 'income_sources',
            'expense': 'monthly_expenses',
            'asset': 'assets',
            'debt': 'debts',
            'children': 'children',
            'support': 'support_payments',
            'deductions': 'deductions'
        }
        
        return variable_names.get(table_type, f'{table_type}_table')
    
    def _get_da_element_type(self, table_type: str) -> str:
        """
        Get docassemble element type for table rows
        """
        element_types = {
            'income': 'IncomeItem',
            'expense': 'ExpenseItem',
            'asset': 'Asset',
            'debt': 'Debt',
            'children': 'Individual',
            'support': 'SupportPayment'
        }
        
        return element_types.get(table_type, 'DAObject')

class ScreenGenerator:
    """
    Generates logical interview screens from fields and tables
    """
    
    def __init__(self):
        # Screen grouping rules
        self.screen_groups = {
            'identification': ['name', 'birthdate', 'sin', 'identification'],
            'contact': ['address', 'phone', 'email', 'contact'],
            'legal': ['court', 'file', 'lawyer', 'lso', 'legal'],
            'marriage': ['marriage', 'separation', 'divorce', 'relationship'],
            'financial': ['income', 'expense', 'asset', 'debt', 'financial'],
            'children': ['child', 'dependent', 'custody', 'access'],
            'support': ['support', 'alimony', 'maintenance', 'payment'],
            'other': []
        }
        
        self.max_fields_per_screen = 7  # Optimal for user experience
    
    def generate_screens(self, 
                        validated_fields: List,
                        tables: List[TableStructure]) -> List[ScreenGroup]:
        """
        Generate logical interview screens
        """
        logger.info("Generating interview screens...")
        
        screens = []
        
        # Group fields by logical categories
        field_groups = self._group_fields_by_category(validated_fields)
        
        # Create screens for regular fields
        for category, fields in field_groups.items():
            category_screens = self._create_field_screens(category, fields)
            screens.extend(category_screens)
        
        # Create screens for tables
        table_screens = self._create_table_screens(tables)
        screens.extend(table_screens)
        
        # Add review screen
        review_screen = self._create_review_screen(screens)
        screens.append(review_screen)
        
        # Add signature screen
        signature_screen = self._create_signature_screen()
        screens.append(signature_screen)
        
        # Sort screens by logical flow
        screens = self._sort_screens_by_flow(screens)
        
        logger.info(f"Generated {len(screens)} interview screens")
        
        return screens
    
    def _group_fields_by_category(self, fields: List) -> Dict[str, List]:
        """
        Group fields into logical categories
        """
        groups = defaultdict(list)
        
        for field_obj in fields:
            label = str(getattr(field_obj, 'field_label', '')).lower()
            name = str(getattr(field_obj, 'canonical_name', '')).lower()
            
            # Find matching category
            matched = False
            for category, keywords in self.screen_groups.items():
                if any(kw in label or kw in name for kw in keywords):
                    groups[category].append(field_obj)
                    matched = True
                    break
            
            if not matched:
                groups['other'].append(field_obj)
        
        return groups
    
    def _create_field_screens(self, category: str, fields: List) -> List[ScreenGroup]:
        """
        Create screens for regular fields
        """
        screens = []
        
        # Split into manageable chunks
        for i in range(0, len(fields), self.max_fields_per_screen):
            chunk = fields[i:i + self.max_fields_per_screen]
            
            screen = ScreenGroup(
                screen_id=f"{category}_{i // self.max_fields_per_screen + 1}",
                title=self._get_screen_title(category, i == 0),
                subtitle=self._get_screen_subtitle(category),
                page_number=getattr(chunk[0], 'page_number', 0) if chunk else 0
            )
            
            # Add fields to screen
            for field_obj in chunk:
                field_config = {
                    'label': getattr(field_obj, 'field_label', ''),
                    'field': getattr(field_obj, 'docassemble_path', ''),
                    'datatype': self._map_to_da_datatype(getattr(field_obj, 'field_type', 'text')),
                    'required': getattr(field_obj, 'required', False)
                }
                
                # Add validation if present
                validation_rules = getattr(field_obj, 'validation_rules', [])
                if validation_rules:
                    field_config['validation'] = validation_rules[0]
                
                # Add help text for Ontario-specific fields
                if getattr(field_obj, 'ontario_specific', False):
                    field_config['help'] = self._get_ontario_help_text(field_obj)
                
                screen.fields.append(field_config)
            
            screens.append(screen)
        
        return screens
    
    def _create_table_screens(self, tables: List[TableStructure]) -> List[ScreenGroup]:
        """
        Create screens for tables
        """
        screens = []
        
        for table in tables:
            screen = ScreenGroup(
                screen_id=f"table_{table.table_id}",
                title=table.table_name,
                subtitle=f"Please provide information for each {table.table_type}",
                page_number=table.page_number,
                question_type='table'
            )
            
            screen.tables.append(table)
            
            # Generate docassemble table configuration
            table_config = self._generate_table_config(table)
            screen.fields.append(table_config)
            
            screens.append(screen)
        
        return screens
    
    def _generate_table_config(self, table: TableStructure) -> Dict:
        """
        Generate docassemble table configuration
        """
        config = {
            'label': table.table_name,
            'field': table.da_variable_name,
            'datatype': 'table',
            'table': {
                'rows': table.da_variable_name,
                'columns': [],
                'show_row_numbers': True,
                'allow_add': table.is_repeating,
                'allow_delete': table.is_repeating,
                'allow_reorder': True
            }
        }
        
        # Add column definitions
        for col in table.columns:
            col_config = {
                'label': col['label'],
                'field': f"row.{col['name']}",
                'datatype': self._map_to_da_datatype(col['type']),
                'required': col.get('required', False)
            }
            
            # Add specific configurations for financial columns
            if col['type'] == 'currency':
                col_config['currency'] = True
                col_config['min'] = 0
            elif col['type'] == 'date':
                col_config['date_format'] = 'MM/dd/yyyy'
            
            config['table']['columns'].append(col_config)
        
        # Add table-specific validations
        if table.table_type == 'income':
            config['validation'] = 'validate_income_table'
        elif table.table_type == 'expense':
            config['validation'] = 'validate_expense_table'
        
        return config
    
    def _create_review_screen(self, screens: List[ScreenGroup]) -> ScreenGroup:
        """
        Create a review screen for all information
        """
        review = ScreenGroup(
            screen_id='review',
            title='Review Your Information',
            subtitle='Please review all information before submitting',
            question_type='review',
            mandatory=True
        )
        
        # Add review sections for each screen
        for screen in screens:
            if screen.question_type != 'review' and screen.screen_id != 'signature':
                review.fields.append({
                    'section': screen.title,
                    'screen_id': screen.screen_id,
                    'editable': True
                })
        
        return review
    
    def _create_signature_screen(self) -> ScreenGroup:
        """
        Create signature screen
        """
        return ScreenGroup(
            screen_id='signature',
            title='Sign and Submit',
            subtitle='By signing below, you certify that the information provided is true and complete',
            question_type='signature',
            mandatory=True,
            fields=[
                {
                    'label': 'Signature',
                    'field': 'users[0].signature',
                    'datatype': 'signature',
                    'required': True
                },
                {
                    'label': 'Date',
                    'field': 'signature_date',
                    'datatype': 'date',
                    'default': 'today',
                    'required': True
                }
            ]
        )
    
    def _sort_screens_by_flow(self, screens: List[ScreenGroup]) -> List[ScreenGroup]:
        """
        Sort screens in logical interview flow
        """
        # Define screen order
        order = [
            'identification',
            'contact',
            'legal',
            'marriage',
            'children',
            'financial',
            'support',
            'other',
            'table',
            'review',
            'signature'
        ]
        
        # Sort screens
        def sort_key(screen):
            for i, prefix in enumerate(order):
                if screen.screen_id.startswith(prefix):
                    return (i, screen.page_number)
            return (len(order), screen.page_number)
        
        return sorted(screens, key=sort_key)
    
    def _get_screen_title(self, category: str, is_first: bool) -> str:
        """
        Get screen title for category
        """
        titles = {
            'identification': 'Personal Information',
            'contact': 'Contact Information',
            'legal': 'Legal Information',
            'marriage': 'Marriage Information',
            'financial': 'Financial Information',
            'children': 'Children Information',
            'support': 'Support Information',
            'other': 'Additional Information'
        }
        
        title = titles.get(category, 'Information')
        if not is_first:
            title += " (Continued)"
        
        return title
    
    def _get_screen_subtitle(self, category: str) -> str:
        """
        Get screen subtitle for category
        """
        subtitles = {
            'identification': 'Please provide your personal details',
            'contact': 'How can we reach you?',
            'legal': 'Court and legal representation information',
            'marriage': 'Information about your marriage or relationship',
            'financial': 'Your income, expenses, assets, and debts',
            'children': 'Information about children involved',
            'support': 'Support payment information',
            'other': 'Any additional required information'
        }
        
        return subtitles.get(category, 'Please provide the following information')
    
    def _map_to_da_datatype(self, field_type: str) -> str:
        """
        Map field type to docassemble datatype
        """
        mapping = {
            'text': 'text',
            'email': 'email',
            'phone': 'phone',
            'date': 'date',
            'currency': 'currency',
            'checkbox': 'yesno',
            'radio': 'radio',
            'select': 'dropdown',
            'signature': 'signature',
            'number': 'number'
        }
        
        return mapping.get(field_type, 'text')
    
    def _get_ontario_help_text(self, field_obj) -> str:
        """
        Get help text for Ontario-specific fields
        """
        name = str(getattr(field_obj, 'canonical_name', '')).lower()
        
        help_texts = {
            'postal_code': 'Enter Canadian postal code (e.g., M5H 2N2)',
            'sin': 'Social Insurance Number (9 digits)',
            'lso_number': 'Law Society of Ontario number (5 digits plus optional letter)',
            'court_file_number': 'Court file number format: XX-##-######'
        }
        
        for key, text in help_texts.items():
            if key in name:
                return text
        
        return ""

class DocassembleInterviewGenerator:
    """
    Generates complete docassemble interview YAML
    """
    
    def __init__(self):
        self.yaml_template = {
            'metadata': {},
            'modules': [],
            'imports': [],
            'objects': {},
            'mandatory': [],
            'code': [],
            'question': [],
            'review': [],
            'attachment': []
        }
    
    def generate_interview(self,
                          screens: List[ScreenGroup],
                          tables: List[TableStructure],
                          form_name: str = "Ontario Family Law Form") -> str:
        """
        Generate complete docassemble interview YAML
        """
        logger.info(f"Generating docassemble interview: {form_name}")
        
        interview = []
        
        # Add metadata
        interview.append(self._generate_metadata(form_name))
        
        # Add imports and modules
        interview.append(self._generate_imports())
        
        # Add object definitions
        interview.append(self._generate_objects(tables))
        
        # Add mandatory code block
        interview.append(self._generate_mandatory_block(screens))
        
        # Generate questions for each screen
        for screen in screens:
            if screen.question_type == 'table':
                interview.append(self._generate_table_question(screen))
            elif screen.question_type == 'review':
                interview.append(self._generate_review_screen(screen))
            elif screen.question_type == 'signature':
                interview.append(self._generate_signature_screen(screen))
            else:
                interview.append(self._generate_field_question(screen))
        
        # Add table management code
        for table in tables:
            interview.append(self._generate_table_code(table))
        
        # Add validation code
        interview.append(self._generate_validation_code())
        
        # Add attachment generation
        interview.append(self._generate_attachment(form_name))
        
        # Combine all sections
        yaml_content = '\n---\n'.join(interview)
        
        return yaml_content
    
    def _generate_metadata(self, form_name: str) -> str:
        """
        Generate metadata section
        """
        metadata = {
            'title': form_name,
            'short_title': form_name.replace('Ontario Family Law ', ''),
            'authors': [
                {'name': 'Auto-generated', 'organization': 'Ontario Family Law System'}
            ],
            'revision_date': '2024-01-01',
            'tags': ['family law', 'ontario', 'auto-generated']
        }
        
        return f"metadata:\n{yaml.dump(metadata, indent=2)}"
    
    def _generate_imports(self) -> str:
        """
        Generate imports section
        """
        imports = """
modules:
  - docassemble.base.util
  - docassemble.base.legal

imports:
  - datetime
  - re
"""
        return imports.strip()
    
    def _generate_objects(self, tables: List[TableStructure]) -> str:
        """
        Generate object definitions
        """
        objects = ['objects:']
        
        # Standard objects
        objects.append('  - users: DAList.using(object_type=Individual)')
        objects.append('  - court: DAObject')
        
        # Table objects
        for table in tables:
            objects.append(f'  - {table.da_variable_name}: DAList.using(object_type={table.da_element_type})')
        
        return '\n'.join(objects)
    
    def _generate_mandatory_block(self, screens: List[ScreenGroup]) -> str:
        """
        Generate mandatory code block that controls interview flow
        """
        code = ['mandatory: True', 'code: |']
        
        # Add screen progression
        for screen in screens:
            if screen.depends_on:
                code.append(f'  if {screen.depends_on}:')
                code.append(f'    {screen.screen_id}_complete')
            else:
                code.append(f'  {screen.screen_id}_complete')
        
        # Final actions
        code.append('  final_screen')
        
        return '\n'.join(code)
    
    def _generate_field_question(self, screen: ScreenGroup) -> str:
        """
        Generate a regular field question
        """
        question = [f'question: {screen.title}']
        
        if screen.subtitle:
            question.append(f'subquestion: {screen.subtitle}')
        
        question.append('fields:')
        
        for field in screen.fields:
            # Basic field definition
            field_def = [f'  - {field["label"]}: {field["field"]}']
            
            # Add field properties
            if field.get('datatype') != 'text':
                field_def.append(f'    datatype: {field["datatype"]}')
            
            if field.get('required'):
                field_def.append('    required: True')
            
            if field.get('validation'):
                field_def.append(f'    validation: {field["validation"]}')
            
            if field.get('help'):
                field_def.append(f'    help: {field["help"]}')
            
            question.extend(field_def)
        
        # Mark screen as complete
        question.append(f'continue button field: {screen.screen_id}_complete')
        
        return '\n'.join(question)
    
    def _generate_table_question(self, screen: ScreenGroup) -> str:
        """
        Generate a table question
        """
        if not screen.tables:
            return ""
        
        table = screen.tables[0]
        
        question = [
            f'question: {screen.title}',
            f'subquestion: {screen.subtitle}',
            'fields:',
            f'  - no label: {table.da_variable_name}.table',
            '    table:',
            f'      - Column: |',
        ]
        
        # Add column headers
        for col in table.columns:
            question.append(f'          {col["label"]}')
        
        question.append(f'      - rows: {table.da_variable_name}')
        question.append('        edit:')
        
        # Add column fields
        for col in table.columns:
            col_name = col['name']
            question.append(f'          - row.{col_name}')
        
        # Table controls
        if table.is_repeating:
            question.extend([
                '        delete buttons: True',
                '        add another label: Add another row'
            ])
        
        question.append(f'continue button field: {screen.screen_id}_complete')
        
        return '\n'.join(question)
    
    def _generate_review_screen(self, screen: ScreenGroup) -> str:
        """
        Generate review screen
        """
        review = [
            'review:',
            '  - Edit your answers:',
            '    review:'
        ]
        
        for field in screen.fields:
            review.append(f'      - {field["section"]}:')
            review.append(f'          edit: {field["screen_id"]}_complete')
        
        review.append(f'continue button field: {screen.screen_id}_complete')
        
        return '\n'.join(review)
    
    def _generate_signature_screen(self, screen: ScreenGroup) -> str:
        """
        Generate signature screen
        """
        signature = [
            f'question: {screen.title}',
            f'subquestion: {screen.subtitle}',
            'signature: users[0].signature',
            'under: |',
            '  **Signature of ${users[0].name.full()}**',
            '  ',
            '  Date: ${signature_date}',
            f'continue button field: {screen.screen_id}_complete'
        ]
        
        return '\n'.join(signature)
    
    def _generate_table_code(self, table: TableStructure) -> str:
        """
        Generate code for table management
        """
        code = [
            'code: |',
            f'  {table.da_variable_name}.gathered = True'
        ]
        
        # Add initialization if needed
        if table.rows:
            code.append(f'  if not {table.da_variable_name}.there_are_any:')
            for row in table.rows[:3]:  # Add first 3 rows as examples
                code.append(f'    {table.da_variable_name}.appendObject()')
                for key, value in row.get('data', {}).items():
                    if isinstance(value, dict) and value.get('value'):
                        code.append(f'    {table.da_variable_name}[-1].{key} = "{value["value"]}"')
                    elif isinstance(value, str) and value:
                        code.append(f'    {table.da_variable_name}[-1].{key} = "{value}"')
        
        return '\n'.join(code)
    
    def _generate_validation_code(self) -> str:
        """
        Generate validation functions
        """
        validation = """
code: |
  def validate_income_table():
    # Ensure at least one income source
    if len(income_sources) == 0:
      validation_error("Please add at least one income source")
    return True
  
  def validate_expense_table():
    # Ensure expenses are reasonable
    total = sum(float(e.amount) for e in monthly_expenses if hasattr(e, 'amount'))
    if total < 0:
      validation_error("Total expenses cannot be negative")
    return True
"""
        return validation.strip()
    
    def _generate_attachment(self, form_name: str) -> str:
        """
        Generate attachment (PDF output)
        """
        attachment = f"""
attachment:
  name: {form_name}
  filename: {form_name.lower().replace(' ', '_')}
  variable name: form_attachment
  content: |
    # {form_name}
    
    % for user in users:
    ## ${{user.name.full()}}
    
    **Contact Information:**
    - Address: ${{user.address}}
    - Phone: ${{user.phone_number}}
    - Email: ${{user.email}}
    % endfor
    
    % if defined('income_sources'):
    ## Income Sources
    % for income in income_sources:
    - ${{income.description}}: $${{income.amount}}
    % endfor
    % endif
"""
        return attachment.strip()

def generate_complete_interview(validated_fields: List,
                               form_name: str = "Ontario Family Law Form",
                               output_dir: str = "generated_interviews") -> Dict:
    """
    Generate complete docassemble interview from validated fields
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("DOCASSEMBLE INTERVIEW GENERATION")
    print("=" * 80)
    
    # Step 1: Detect tables
    print("\n1. DETECTING TABLES")
    print("-" * 40)
    
    detector = TableDetector()
    tables = detector.detect_tables(validated_fields)
    
    print(f"Tables detected: {len(tables)}")
    for table in tables:
        print(f"  - {table.table_name}: {len(table.columns)} columns, {len(table.rows)} rows")
    
    # Step 2: Generate screens
    print("\n2. GENERATING SCREENS")
    print("-" * 40)
    
    generator = ScreenGenerator()
    screens = generator.generate_screens(validated_fields, tables)
    
    print(f"Screens generated: {len(screens)}")
    for screen in screens:
        field_count = len(screen.fields) + len(screen.tables)
        print(f"  - {screen.title}: {field_count} items ({screen.question_type})")
    
    # Step 3: Generate YAML
    print("\n3. GENERATING YAML INTERVIEW")
    print("-" * 40)
    
    interview_gen = DocassembleInterviewGenerator()
    yaml_content = interview_gen.generate_interview(screens, tables, form_name)
    
    # Save outputs
    yaml_file = output_path / f"{form_name.lower().replace(' ', '_')}.yml"
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
    
    # Save table definitions
    tables_file = output_path / "tables.json"
    with open(tables_file, 'w') as f:
        json.dump([asdict(t) for t in tables], f, indent=2)
    
    # Save screen definitions
    screens_file = output_path / "screens.json"
    with open(screens_file, 'w') as f:
        json.dump([asdict(s) for s in screens], f, indent=2)
    
    print(f"\nFiles generated:")
    print(f"  - {yaml_file}")
    print(f"  - {tables_file}")
    print(f"  - {screens_file}")
    
    # Generate summary
    summary = {
        'form_name': form_name,
        'total_fields': len(validated_fields),
        'tables_generated': len(tables),
        'screens_generated': len(screens),
        'files': {
            'interview': str(yaml_file),
            'tables': str(tables_file),
            'screens': str(screens_file)
        },
        'statistics': {
            'fields_per_screen': len(validated_fields) / max(1, len(screens) - 2),  # Exclude review/signature
            'table_fields': sum(len(t.columns) * len(t.rows) for t in tables),
            'regular_fields': len(validated_fields) - sum(len(t.columns) * len(t.rows) for t in tables)
        }
    }
    
    return summary

if __name__ == "__main__":
    # Test with sample validated fields
    from field_validation_mapper import ValidatedField
    
    # Create sample fields including table data
    sample_fields = [
        ValidatedField(
            field_id='1',
            canonical_name='full_legal_name',
            field_type='text',
            field_label='Full Legal Name',
            docassemble_object='Individual',
            docassemble_path='users[0].name.text',
            page_number=1
        ),
        ValidatedField(
            field_id='2',
            canonical_name='income_employment',
            field_type='currency',
            field_label='1. Income from employment',
            docassemble_object='Value',
            docassemble_path='income[0]',
            page_number=5,
            context='Row 1'
        ),
        ValidatedField(
            field_id='3',
            canonical_name='income_investment',
            field_type='currency',
            field_label='2. Investment income',
            docassemble_object='Value',
            docassemble_path='income[1]',
            page_number=5,
            context='Row 2'
        ),
        ValidatedField(
            field_id='4',
            canonical_name='income_other',
            field_type='currency',
            field_label='3. Other income',
            docassemble_object='Value',
            docassemble_path='income[2]',
            page_number=5,
            context='Row 3'
        )
    ]
    
    # Generate interview
    summary = generate_complete_interview(
        sample_fields,
        "Form 13 - Financial Statement"
    )
    
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(json.dumps(summary, indent=2))