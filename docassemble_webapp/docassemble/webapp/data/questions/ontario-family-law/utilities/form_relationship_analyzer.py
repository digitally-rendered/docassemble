#!/usr/bin/env python3
"""
Form Relationship Analyzer
Reconciles multiple parsing methods and identifies field relationships, tables, and entities
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FieldSource:
    """Track where a field was detected"""
    method: str  # 'legacy', 'pattern', 'widget', 'table'
    confidence: float  # 0.0 to 1.0
    context: str
    metadata: Dict = field(default_factory=dict)

@dataclass
class ReconciledField:
    """A field reconciled from multiple sources"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    sources: List[FieldSource]
    
    # Structural information
    table_id: Optional[str] = None
    table_row: Optional[int] = None
    table_col: Optional[int] = None
    group_id: Optional[str] = None
    entity_type: Optional[str] = None  # 'person', 'address', 'financial', etc.
    
    # Relationships
    related_fields: List[str] = field(default_factory=list)
    parent_field: Optional[str] = None
    child_fields: List[str] = field(default_factory=list)
    
    # Validation and constraints
    required: bool = False
    validation_rules: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    
    # Position and layout
    page_number: Optional[int] = None
    section: Optional[str] = None
    order: Optional[int] = None

@dataclass
class TableStructure:
    """Represents a table in the form"""
    table_id: str
    table_name: str
    table_type: str  # 'list', 'matrix', 'details'
    rows: int
    cols: int
    headers: List[str]
    fields: List[str]  # Field IDs in this table
    repeating: bool = False
    entity_per_row: bool = False

@dataclass
class FormEntity:
    """Represents an entity in the form (person, property, etc.)"""
    entity_id: str
    entity_type: str
    entity_name: str
    fields: List[str]  # Field IDs belonging to this entity
    cardinality: str  # 'single', 'multiple', 'list'
    parent_entity: Optional[str] = None

@dataclass
class FormRelationship:
    """Represents relationships between forms"""
    source_form: str
    target_form: str
    relationship_type: str  # 'prerequisite', 'companion', 'followup', 'alternative'
    shared_fields: List[str]
    data_flow: str  # 'unidirectional', 'bidirectional'

class FormRelationshipAnalyzer:
    """Analyzes and reconciles form fields from multiple parsing methods"""
    
    def __init__(self, enhanced_parsed_dir: str = "workflow_output/enhanced_parsed_forms"):
        self.parsed_dir = Path(enhanced_parsed_dir)
        self.forms = {}
        self.entities = {}
        self.tables = {}
        self.relationships = []
        
    def analyze_all_forms(self):
        """Main analysis pipeline"""
        logger.info("Starting comprehensive form analysis...")
        
        # 1. Load all parsed forms
        self._load_parsed_forms()
        
        # 2. Reconcile fields from different sources
        self._reconcile_fields()
        
        # 3. Identify table structures
        self._identify_tables()
        
        # 4. Detect entities
        self._detect_entities()
        
        # 5. Find field relationships
        self._find_field_relationships()
        
        # 6. Analyze cross-form relationships
        self._analyze_cross_form_relationships()
        
        # 7. Generate report
        self._generate_analysis_report()
        
        logger.info("Analysis complete!")
    
    def _load_parsed_forms(self):
        """Load all parsed form data"""
        for json_file in self.parsed_dir.glob("form_*_fields.json"):
            form_number = json_file.stem.replace('form_', '').replace('_fields', '')
            
            with open(json_file, 'r') as f:
                fields_data = json.load(f)
            
            self.forms[form_number] = {
                'raw_fields': fields_data,
                'reconciled_fields': {},
                'tables': [],
                'entities': [],
                'field_groups': defaultdict(list)
            }
            
        logger.info(f"Loaded {len(self.forms)} forms")
    
    def _reconcile_fields(self):
        """Reconcile fields from different parsing methods"""
        for form_num, form_data in self.forms.items():
            reconciled = {}
            field_clusters = defaultdict(list)
            
            # Group fields by similar names/positions
            for field_data in form_data['raw_fields']:
                # Create a clustering key based on field characteristics
                cluster_key = self._get_cluster_key(field_data)
                field_clusters[cluster_key].append(field_data)
            
            # Reconcile each cluster into a single field
            for cluster_key, cluster_fields in field_clusters.items():
                reconciled_field = self._merge_field_cluster(cluster_fields)
                reconciled[reconciled_field.field_id] = reconciled_field
            
            form_data['reconciled_fields'] = reconciled
            logger.info(f"Form {form_num}: Reconciled {len(form_data['raw_fields'])} raw fields into {len(reconciled)} unique fields")
    
    def _get_cluster_key(self, field_data: Dict) -> str:
        """Generate a clustering key for field grouping"""
        # Extract key characteristics
        name = field_data.get('field_name', '').lower()
        label = field_data.get('field_label', '').lower()
        context = field_data.get('field_context', '').lower()
        
        # Normalize common variations
        name = re.sub(r'[_\d]+$', '', name)  # Remove trailing numbers
        name = re.sub(r'field_', '', name)  # Remove generic prefixes
        
        # Combine for clustering
        if 'table' in context:
            # Table fields cluster by table and row
            table_info = f"{field_data.get('table_name', '')}_{field_data.get('table_row', 0)}"
            return f"table_{table_info}_{name}"
        elif 'legacy' in field_data.get('field_id', ''):
            # Legacy fields cluster by exact name
            return f"legacy_{name}"
        else:
            # Pattern-based fields cluster by label similarity
            label_key = re.sub(r'[^a-z]+', '', label[:20])
            return f"pattern_{label_key}"
    
    def _merge_field_cluster(self, cluster_fields: List[Dict]) -> ReconciledField:
        """Merge a cluster of similar fields into one reconciled field"""
        # Start with the most reliable source
        primary = self._select_primary_field(cluster_fields)
        
        # Create reconciled field
        reconciled = ReconciledField(
            field_id=primary.get('field_id', f"field_{id(cluster_fields)}"),
            field_name=primary.get('field_name', 'unknown'),
            field_type=primary.get('field_type', 'text'),
            field_label=primary.get('field_label', ''),
            sources=[]
        )
        
        # Add source information
        for field_data in cluster_fields:
            source = FieldSource(
                method=self._detect_parsing_method(field_data),
                confidence=self._calculate_confidence(field_data),
                context=field_data.get('field_context', ''),
                metadata={
                    'original_id': field_data.get('field_id'),
                    'help_text': field_data.get('help_text'),
                    'options': field_data.get('options')
                }
            )
            reconciled.sources.append(source)
        
        # Extract structural information
        if primary.get('table_name'):
            reconciled.table_id = primary.get('table_name')
            reconciled.table_row = primary.get('table_row')
            
        reconciled.page_number = primary.get('page_number')
        reconciled.required = primary.get('required', False)
        
        return reconciled
    
    def _select_primary_field(self, cluster_fields: List[Dict]) -> Dict:
        """Select the most reliable field from a cluster"""
        # Priority: legacy fields > widget fields > pattern fields
        for field_data in cluster_fields:
            if 'legacy' in field_data.get('field_id', ''):
                return field_data
        
        for field_data in cluster_fields:
            if 'widget' in field_data.get('field_id', ''):
                return field_data
                
        return cluster_fields[0]
    
    def _detect_parsing_method(self, field_data: Dict) -> str:
        """Detect which parsing method found this field"""
        field_id = field_data.get('field_id', '')
        context = field_data.get('field_context', '')
        
        if 'legacy' in field_id:
            return 'legacy'
        elif 'widget' in field_id:
            return 'widget'
        elif 'table' in context.lower():
            return 'table'
        else:
            return 'pattern'
    
    def _calculate_confidence(self, field_data: Dict) -> float:
        """Calculate confidence score for a field detection"""
        confidence = 0.5
        
        # Legacy fields are most reliable
        if 'legacy' in field_data.get('field_id', ''):
            confidence = 0.95
        # Widget fields are very reliable
        elif 'widget' in field_data.get('field_id', ''):
            confidence = 0.9
        # Fields with help text are more reliable
        elif field_data.get('help_text'):
            confidence = 0.8
        # Named fields are more reliable than generic
        elif not field_data.get('field_name', '').startswith('field_'):
            confidence = 0.7
            
        return confidence
    
    def _identify_tables(self):
        """Identify table structures in forms"""
        for form_num, form_data in self.forms.items():
            tables = defaultdict(lambda: {'fields': [], 'rows': set(), 'cols': set()})
            
            for field_id, field in form_data['reconciled_fields'].items():
                if field.table_id:
                    tables[field.table_id]['fields'].append(field_id)
                    if field.table_row is not None:
                        tables[field.table_id]['rows'].add(field.table_row)
                    if field.table_col is not None:
                        tables[field.table_id]['cols'].add(field.table_col)
            
            # Create TableStructure objects
            for table_id, table_info in tables.items():
                table_struct = self._analyze_table_structure(
                    table_id, 
                    table_info,
                    form_data['reconciled_fields']
                )
                form_data['tables'].append(table_struct)
                self.tables[f"{form_num}_{table_id}"] = table_struct
            
            if form_data['tables']:
                logger.info(f"Form {form_num}: Identified {len(form_data['tables'])} tables")
    
    def _analyze_table_structure(self, table_id: str, table_info: Dict, fields: Dict) -> TableStructure:
        """Analyze the structure of a table"""
        table_fields = table_info['fields']
        rows = len(table_info['rows']) if table_info['rows'] else 1
        cols = len(table_info['cols']) if table_info['cols'] else 1
        
        # Detect table type
        table_type = 'details'  # default
        
        # Check if it's a list (repeating rows with same structure)
        if rows > 2:
            row_patterns = defaultdict(list)
            for field_id in table_fields:
                field = fields[field_id]
                pattern = self._get_field_pattern(field)
                row_patterns[field.table_row].append(pattern)
            
            # If rows have similar patterns, it's likely a list
            if len(set(tuple(p) for p in row_patterns.values())) <= 2:
                table_type = 'list'
        
        # Check if it's a matrix (grid of similar fields)
        if rows > 1 and cols > 1:
            field_types = [fields[fid].field_type for fid in table_fields]
            if len(set(field_types)) <= 2:
                table_type = 'matrix'
        
        return TableStructure(
            table_id=table_id,
            table_name=table_id,
            table_type=table_type,
            rows=rows,
            cols=cols,
            headers=self._extract_table_headers(table_fields, fields),
            fields=table_fields,
            repeating=(table_type == 'list'),
            entity_per_row=(table_type == 'list')
        )
    
    def _get_field_pattern(self, field: ReconciledField) -> str:
        """Get a pattern signature for a field"""
        return f"{field.field_type}_{field.field_label[:10]}"
    
    def _extract_table_headers(self, field_ids: List[str], fields: Dict) -> List[str]:
        """Extract table headers from first row fields"""
        headers = []
        row_0_fields = [fields[fid] for fid in field_ids if fields[fid].table_row == 0]
        
        for field in sorted(row_0_fields, key=lambda f: f.table_col or 0):
            headers.append(field.field_label)
        
        return headers
    
    def _detect_entities(self):
        """Detect logical entities in forms"""
        for form_num, form_data in self.forms.items():
            entities = []
            
            # Detect person entities
            person_entities = self._detect_person_entities(form_data['reconciled_fields'])
            entities.extend(person_entities)
            
            # Detect property/asset entities
            property_entities = self._detect_property_entities(form_data['reconciled_fields'])
            entities.extend(property_entities)
            
            # Detect financial entities
            financial_entities = self._detect_financial_entities(form_data['reconciled_fields'])
            entities.extend(financial_entities)
            
            # Detect from table structures
            for table in form_data['tables']:
                if table.entity_per_row:
                    table_entities = self._extract_table_entities(table, form_data['reconciled_fields'])
                    entities.extend(table_entities)
            
            form_data['entities'] = entities
            for entity in entities:
                self.entities[f"{form_num}_{entity.entity_id}"] = entity
            
            if entities:
                logger.info(f"Form {form_num}: Detected {len(entities)} entities")
    
    def _detect_person_entities(self, fields: Dict) -> List[FormEntity]:
        """Detect person-related entities"""
        entities = []
        person_groups = defaultdict(list)
        
        person_keywords = ['name', 'birth', 'address', 'phone', 'email', 'sin', 'occupation']
        role_keywords = ['applicant', 'respondent', 'child', 'spouse', 'parent']
        
        for field_id, field in fields.items():
            label_lower = field.field_label.lower()
            
            # Check for role indicators
            role = None
            for keyword in role_keywords:
                if keyword in label_lower:
                    role = keyword
                    break
            
            if not role:
                role = 'person'
            
            # Check if it's a person field
            for keyword in person_keywords:
                if keyword in label_lower:
                    person_groups[role].append(field_id)
                    break
        
        # Create entities for each person group
        for role, field_ids in person_groups.items():
            if len(field_ids) >= 2:  # Need at least 2 fields to be an entity
                entity = FormEntity(
                    entity_id=f"{role}_entity",
                    entity_type='person',
                    entity_name=role.title(),
                    fields=field_ids,
                    cardinality='single' if role != 'child' else 'multiple'
                )
                entities.append(entity)
        
        return entities
    
    def _detect_property_entities(self, fields: Dict) -> List[FormEntity]:
        """Detect property/asset entities"""
        entities = []
        property_groups = defaultdict(list)
        
        property_keywords = ['property', 'asset', 'real estate', 'vehicle', 'bank', 'investment']
        
        for field_id, field in fields.items():
            label_lower = field.field_label.lower()
            
            for keyword in property_keywords:
                if keyword in label_lower:
                    property_groups[keyword].append(field_id)
                    break
        
        for prop_type, field_ids in property_groups.items():
            if len(field_ids) >= 2:
                entity = FormEntity(
                    entity_id=f"{prop_type.replace(' ', '_')}_entity",
                    entity_type='property',
                    entity_name=prop_type.title(),
                    fields=field_ids,
                    cardinality='multiple'
                )
                entities.append(entity)
        
        return entities
    
    def _detect_financial_entities(self, fields: Dict) -> List[FormEntity]:
        """Detect financial entities"""
        entities = []
        financial_groups = defaultdict(list)
        
        financial_keywords = ['income', 'expense', 'debt', 'payment', 'support', 'amount']
        
        for field_id, field in fields.items():
            label_lower = field.field_label.lower()
            
            for keyword in financial_keywords:
                if keyword in label_lower:
                    financial_groups[keyword].append(field_id)
                    break
        
        for fin_type, field_ids in financial_groups.items():
            if len(field_ids) >= 3:
                entity = FormEntity(
                    entity_id=f"{fin_type}_entity",
                    entity_type='financial',
                    entity_name=f"{fin_type.title()} Information",
                    fields=field_ids,
                    cardinality='single'
                )
                entities.append(entity)
        
        return entities
    
    def _extract_table_entities(self, table: TableStructure, fields: Dict) -> List[FormEntity]:
        """Extract entities from table structures"""
        entities = []
        
        if table.entity_per_row and table.rows > 1:
            # Each row (except header) is an entity
            row_entities = defaultdict(list)
            
            for field_id in table.fields:
                field = fields[field_id]
                if field.table_row and field.table_row > 0:
                    row_entities[field.table_row].append(field_id)
            
            for row_num, row_fields in row_entities.items():
                entity = FormEntity(
                    entity_id=f"{table.table_id}_row_{row_num}",
                    entity_type='table_row',
                    entity_name=f"{table.table_name} Item {row_num}",
                    fields=row_fields,
                    cardinality='single',
                    parent_entity=table.table_id
                )
                entities.append(entity)
        
        return entities
    
    def _find_field_relationships(self):
        """Find relationships between fields within forms"""
        for form_num, form_data in self.forms.items():
            fields = form_data['reconciled_fields']
            
            for field_id, field in fields.items():
                # Find dependent fields (e.g., "if yes, specify...")
                self._find_conditional_relationships(field, fields)
                
                # Find grouped fields (e.g., address components)
                self._find_grouped_relationships(field, fields)
                
                # Find calculated fields
                self._find_calculated_relationships(field, fields)
    
    def _find_conditional_relationships(self, field: ReconciledField, all_fields: Dict):
        """Find conditional/dependent relationships"""
        label_lower = field.field_label.lower()
        
        # Check for conditional patterns
        if 'if yes' in label_lower or 'if checked' in label_lower:
            # This field depends on another
            for other_id, other_field in all_fields.items():
                if other_field.field_type in ['checkbox', 'radio']:
                    # Simple proximity check
                    if abs((field.page_number or 0) - (other_field.page_number or 0)) <= 1:
                        field.depends_on.append(other_id)
                        other_field.child_fields.append(field.field_id)
                        break
    
    def _find_grouped_relationships(self, field: ReconciledField, all_fields: Dict):
        """Find fields that are part of the same group"""
        label_lower = field.field_label.lower()
        
        # Address components
        if any(word in label_lower for word in ['street', 'city', 'province', 'postal']):
            field.group_id = 'address'
            field.entity_type = 'address'
        
        # Name components
        elif any(word in label_lower for word in ['first name', 'last name', 'middle name']):
            field.group_id = 'full_name'
            field.entity_type = 'person'
        
        # Contact information
        elif any(word in label_lower for word in ['phone', 'email', 'fax']):
            field.group_id = 'contact'
            field.entity_type = 'contact'
    
    def _find_calculated_relationships(self, field: ReconciledField, all_fields: Dict):
        """Find calculated field relationships"""
        label_lower = field.field_label.lower()
        
        # Total/sum fields
        if any(word in label_lower for word in ['total', 'sum', 'subtotal', 'net']):
            # Find potential source fields
            for other_id, other_field in all_fields.items():
                if other_field.field_type in ['currency', 'number']:
                    if other_field.table_id == field.table_id:
                        field.depends_on.append(other_id)
    
    def _analyze_cross_form_relationships(self):
        """Analyze relationships between different forms"""
        form_numbers = list(self.forms.keys())
        
        for i, form1 in enumerate(form_numbers):
            for form2 in form_numbers[i+1:]:
                relationship = self._compare_forms(form1, form2)
                if relationship:
                    self.relationships.append(relationship)
        
        logger.info(f"Identified {len(self.relationships)} cross-form relationships")
    
    def _compare_forms(self, form1: str, form2: str) -> Optional[FormRelationship]:
        """Compare two forms for relationships"""
        fields1 = self.forms[form1]['reconciled_fields']
        fields2 = self.forms[form2]['reconciled_fields']
        
        # Find shared field patterns
        shared_fields = []
        labels1 = {f.field_label.lower() for f in fields1.values()}
        labels2 = {f.field_label.lower() for f in fields2.values()}
        
        common_labels = labels1 & labels2
        
        if len(common_labels) > 5:  # Significant overlap
            relationship_type = self._determine_relationship_type(form1, form2, common_labels)
            
            return FormRelationship(
                source_form=form1,
                target_form=form2,
                relationship_type=relationship_type,
                shared_fields=list(common_labels)[:20],  # Limit for readability
                data_flow='bidirectional'
            )
        
        return None
    
    def _determine_relationship_type(self, form1: str, form2: str, common_labels: Set[str]) -> str:
        """Determine the type of relationship between forms"""
        # Financial forms often go together
        if '13' in form1 and '13' in form2:
            return 'companion'
        
        # Application and response
        elif ('8' in form1 and '10' in form2) or ('10' in form1 and '8' in form2):
            return 'response'
        
        # Motion and response
        elif ('14' in form1 and '15' in form2) or ('15' in form1 and '14' in form2):
            return 'response'
        
        # Default based on form number sequence
        elif abs(int(re.search(r'\d+', form1).group()) - int(re.search(r'\d+', form2).group())) == 1:
            return 'sequential'
        
        else:
            return 'related'
    
    def _generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_forms': len(self.forms),
                'total_fields': sum(len(f['reconciled_fields']) for f in self.forms.values()),
                'total_tables': len(self.tables),
                'total_entities': len(self.entities),
                'total_relationships': len(self.relationships)
            },
            'forms': {},
            'entities': {},
            'tables': {},
            'relationships': []
        }
        
        # Form details
        for form_num, form_data in self.forms.items():
            report['forms'][form_num] = {
                'field_count': len(form_data['reconciled_fields']),
                'table_count': len(form_data['tables']),
                'entity_count': len(form_data['entities']),
                'parsing_methods': self._count_parsing_methods(form_data['reconciled_fields']),
                'field_types': self._count_field_types(form_data['reconciled_fields']),
                'entities': [asdict(e) for e in form_data['entities']],
                'tables': [asdict(t) for t in form_data['tables']]
            }
        
        # Entity catalog
        for entity_id, entity in self.entities.items():
            report['entities'][entity_id] = asdict(entity)
        
        # Table catalog
        for table_id, table in self.tables.items():
            report['tables'][table_id] = asdict(table)
        
        # Relationships
        report['relationships'] = [asdict(r) for r in self.relationships]
        
        # Save report
        output_file = Path('workflow_output/form_relationship_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Analysis report saved to {output_file}")
        
        # Generate markdown summary
        self._generate_markdown_summary(report)
    
    def _count_parsing_methods(self, fields: Dict) -> Dict[str, int]:
        """Count fields by parsing method"""
        counts = defaultdict(int)
        for field in fields.values():
            for source in field.sources:
                counts[source.method] += 1
        return dict(counts)
    
    def _count_field_types(self, fields: Dict) -> Dict[str, int]:
        """Count fields by type"""
        counts = defaultdict(int)
        for field in fields.values():
            counts[field.field_type] += 1
        return dict(counts)
    
    def _generate_markdown_summary(self, report: Dict):
        """Generate a markdown summary of the analysis"""
        md_lines = [
            "# Ontario Family Law Forms - Relationship Analysis Report",
            f"\nGenerated: {report['timestamp']}",
            "\n## Summary Statistics",
            f"- **Total Forms Analyzed**: {report['summary']['total_forms']}",
            f"- **Total Fields Identified**: {report['summary']['total_fields']}",
            f"- **Total Tables Found**: {report['summary']['total_tables']}",
            f"- **Total Entities Detected**: {report['summary']['total_entities']}",
            f"- **Cross-Form Relationships**: {report['summary']['total_relationships']}",
            "\n## Forms Overview\n"
        ]
        
        # Sort forms by field count
        sorted_forms = sorted(
            report['forms'].items(),
            key=lambda x: x[1]['field_count'],
            reverse=True
        )
        
        for form_num, form_info in sorted_forms[:10]:
            md_lines.append(f"\n### Form {form_num}")
            md_lines.append(f"- **Fields**: {form_info['field_count']}")
            md_lines.append(f"- **Tables**: {form_info['table_count']}")
            md_lines.append(f"- **Entities**: {form_info['entity_count']}")
            
            if form_info['field_types']:
                md_lines.append(f"- **Field Types**: {', '.join(f'{k}({v})' for k, v in form_info['field_types'].items())}")
            
            if form_info['entities']:
                md_lines.append("- **Detected Entities**:")
                for entity in form_info['entities'][:5]:
                    md_lines.append(f"  - {entity['entity_name']} ({entity['entity_type']}, {len(entity['fields'])} fields)")
        
        # Key relationships
        if report['relationships']:
            md_lines.append("\n## Key Form Relationships\n")
            for rel in report['relationships'][:10]:
                md_lines.append(f"- **{rel['source_form']} ↔ {rel['target_form']}**: {rel['relationship_type']} ({len(rel['shared_fields'])} shared fields)")
        
        # Save markdown
        md_file = Path('workflow_output/form_relationship_analysis.md')
        with open(md_file, 'w') as f:
            f.write('\n'.join(md_lines))
        
        logger.info(f"Markdown summary saved to {md_file}")

def main():
    """Run the analysis"""
    analyzer = FormRelationshipAnalyzer()
    analyzer.analyze_all_forms()

if __name__ == "__main__":
    main()