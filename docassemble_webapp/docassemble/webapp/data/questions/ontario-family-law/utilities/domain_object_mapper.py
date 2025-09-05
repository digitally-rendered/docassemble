#!/usr/bin/env python3
"""
Domain Object Mapper for Ontario Family Law Forms
Maps detected entities and fields to Docassemble objects and generates appropriate interview structures
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import logging
from docassemble_interview_builder import (
    ObjectDeclaration, FieldDefinition, Question, DataType,
    create_person_object, create_list_object, create_text_field,
    create_currency_field, create_date_field, create_yesno_field,
    create_dropdown_field
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocassembleObjectType(Enum):
    """Standard Docassemble object types"""
    INDIVIDUAL = "Individual"
    PERSON = "Person"
    NAME = "Name"
    INDIVIDUALNAME = "IndividualName"
    ADDRESS = "Address"
    ORGANIZATION = "Organization"
    DAOBJECT = "DAObject"
    DALIST = "DAList"
    DADICT = "DADict"
    DASET = "DASet"
    DAFILE = "DAFile"
    DAFILELIST = "DAFileList"
    DAEMAIL = "DAEmail"
    DAEMAILRECIPIENT = "DAEmailRecipient"
    DATEPERIOD = "DADatePeriod"
    PERIODVALUE = "PeriodValue"
    VALUE = "Value"
    FINANCIALLIST = "FinancialList"
    INCOME = "Income"
    EXPENSE = "Expense"
    ASSET = "Asset"
    LIABILITY = "Liability"


class OntarioEntityType(Enum):
    """Ontario Family Law specific entity types"""
    APPLICANT = "applicant"
    RESPONDENT = "respondent"
    CHILD = "child"
    SPOUSE = "spouse"
    PARENT = "parent"
    PROPERTY = "property"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    BANK_ACCOUNT = "bank_account"
    INVESTMENT = "investment"
    INCOME_SOURCE = "income_source"
    EXPENSE_ITEM = "expense_item"
    DEBT = "debt"
    SUPPORT_PAYMENT = "support_payment"
    COURT_ORDER = "court_order"
    LEGAL_PROCEEDING = "legal_proceeding"


@dataclass
class DomainEntity:
    """Represents a domain entity from form analysis"""
    entity_id: str
    entity_type: str  # person, property, financial, etc.
    entity_name: str
    field_ids: List[str]
    cardinality: str  # single, multiple
    parent_entity: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def get_docassemble_type(self) -> str:
        """Map domain entity to Docassemble object type"""
        mapping = {
            'person': DocassembleObjectType.INDIVIDUAL.value,
            'property': DocassembleObjectType.DAOBJECT.value,
            'financial': DocassembleObjectType.DAOBJECT.value,
            'address': DocassembleObjectType.ADDRESS.value,
            'organization': DocassembleObjectType.ORGANIZATION.value,
            'court': DocassembleObjectType.DAOBJECT.value,
            'table_row': DocassembleObjectType.DAOBJECT.value
        }
        return mapping.get(self.entity_type, DocassembleObjectType.DAOBJECT.value)
    
    def get_variable_name(self) -> str:
        """Get the Docassemble variable name for this entity"""
        # Clean the entity name
        name = self.entity_name.lower().replace(' ', '_')
        
        # Handle specific roles
        if 'applicant' in name:
            return 'applicant'
        elif 'respondent' in name:
            return 'respondent'
        elif 'child' in name:
            return 'children' if self.cardinality == 'multiple' else 'child'
        elif 'spouse' in name:
            return 'spouse'
        elif 'property' in name and self.cardinality == 'multiple':
            return 'properties'
        elif 'asset' in name and self.cardinality == 'multiple':
            return 'assets'
        elif 'debt' in name and self.cardinality == 'multiple':
            return 'debts'
        elif 'income' in name and self.cardinality == 'multiple':
            return 'income_sources'
        elif 'expense' in name and self.cardinality == 'multiple':
            return 'expenses'
        
        # Default: pluralize if multiple
        if self.cardinality == 'multiple' and not name.endswith('s'):
            return name + 's'
        
        return name


@dataclass
class DomainField:
    """Represents a field with its domain context"""
    field_id: str
    field_name: str
    field_type: str
    field_label: str
    entity_id: Optional[str] = None
    table_id: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    required: bool = False
    options: Optional[List[str]] = None
    help_text: Optional[str] = None
    context: Optional[str] = None
    
    def get_docassemble_datatype(self) -> DataType:
        """Map field type to Docassemble datatype"""
        mapping = {
            'text': DataType.TEXT,
            'number': DataType.NUMBER,
            'currency': DataType.CURRENCY,
            'date': DataType.DATE,
            'time': DataType.TIME,
            'datetime': DataType.DATETIME,
            'email': DataType.EMAIL,
            'phone': DataType.TEXT,  # Use text with validation
            'checkbox': DataType.YESNO,
            'radio': DataType.RADIO,
            'dropdown': DataType.COMBOBOX,
            'select': DataType.COMBOBOX,
            'file': DataType.FILE,
            'boolean': DataType.BOOLEAN,
            'yesno': DataType.YESNO,
            'address': DataType.TEXT,  # Could be enhanced
            'sin': DataType.TEXT,  # With validation
            'postal_code': DataType.TEXT  # With validation
        }
        return mapping.get(self.field_type, DataType.TEXT)
    
    def needs_validation(self) -> bool:
        """Check if field needs validation"""
        return self.field_type in ['email', 'phone', 'sin', 'postal_code'] or len(self.validation_rules) > 0


class DomainObjectMapper:
    """Maps domain entities and fields to Docassemble objects"""
    
    def __init__(self, relationship_analysis_file: str = "workflow_output/form_relationship_analysis.json"):
        self.relationship_data = self._load_relationship_data(relationship_analysis_file)
        self.entities: Dict[str, DomainEntity] = {}
        self.fields: Dict[str, DomainField] = {}
        self.object_mappings: Dict[str, ObjectDeclaration] = {}
        self.field_mappings: Dict[str, FieldDefinition] = {}
        
    def _load_relationship_data(self, file_path: str) -> Dict:
        """Load the relationship analysis data"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_form_data(self, form_number: str) -> Tuple[List[DomainEntity], List[DomainField]]:
        """Load and map entities and fields for a specific form"""
        if form_number not in self.relationship_data.get('forms', {}):
            logger.warning(f"Form {form_number} not found in relationship data")
            return [], []
        
        form_data = self.relationship_data['forms'][form_number]
        entities = []
        fields = []
        
        # Load entities
        for entity_data in form_data.get('entities', []):
            entity = DomainEntity(
                entity_id=entity_data['entity_id'],
                entity_type=entity_data['entity_type'],
                entity_name=entity_data['entity_name'],
                field_ids=entity_data['fields'],
                cardinality=entity_data.get('cardinality', 'single'),
                parent_entity=entity_data.get('parent_entity')
            )
            entities.append(entity)
            self.entities[entity.entity_id] = entity
        
        # Load fields from enhanced parsed data
        parsed_file = Path(f"workflow_output/enhanced_parsed_forms/form_{form_number}_fields.json")
        if parsed_file.exists():
            with open(parsed_file, 'r') as f:
                raw_fields = json.load(f)
            
            for field_data in raw_fields:
                domain_field = DomainField(
                    field_id=field_data.get('field_id', ''),
                    field_name=field_data.get('field_name', ''),
                    field_type=field_data.get('field_type', 'text'),
                    field_label=field_data.get('field_label', ''),
                    required=field_data.get('required', False),
                    options=field_data.get('options'),
                    help_text=field_data.get('help_text'),
                    context=field_data.get('field_context')
                )
                
                # Find which entity this field belongs to
                for entity in entities:
                    if domain_field.field_id in entity.field_ids:
                        domain_field.entity_id = entity.entity_id
                        break
                
                fields.append(domain_field)
                self.fields[domain_field.field_id] = domain_field
        
        return entities, fields
    
    def create_object_declarations(self, entities: List[DomainEntity]) -> List[ObjectDeclaration]:
        """Create Docassemble object declarations from domain entities"""
        objects = []
        
        # Always include court info
        objects.append(ObjectDeclaration(
            name="court_info",
            object_type=DocassembleObjectType.DAOBJECT.value
        ))
        
        # Process entities
        for entity in entities:
            var_name = entity.get_variable_name()
            obj_type = entity.get_docassemble_type()
            
            if entity.cardinality == 'multiple':
                obj = create_list_object(var_name, obj_type)
            else:
                obj = ObjectDeclaration(name=var_name, object_type=obj_type)
            
            objects.append(obj)
            self.object_mappings[entity.entity_id] = obj
        
        # Add special Ontario objects if needed
        entity_types = {e.entity_type for e in entities}
        
        if 'financial' in entity_types:
            # Add financial calculation objects
            if 'income_sources' not in [o.name for o in objects]:
                objects.append(create_list_object("income_sources", DocassembleObjectType.INCOME.value))
            if 'expenses' not in [o.name for o in objects]:
                objects.append(create_list_object("expenses", DocassembleObjectType.EXPENSE.value))
            if 'assets' not in [o.name for o in objects]:
                objects.append(create_list_object("assets", DocassembleObjectType.ASSET.value))
            if 'debts' not in [o.name for o in objects]:
                objects.append(create_list_object("debts", DocassembleObjectType.LIABILITY.value))
        
        return objects
    
    def create_field_definitions(self, fields: List[DomainField], entity: Optional[DomainEntity] = None) -> List[FieldDefinition]:
        """Create Docassemble field definitions from domain fields"""
        field_defs = []
        
        for domain_field in fields:
            # Skip if this field doesn't belong to the specified entity
            if entity and domain_field.entity_id != entity.entity_id:
                continue
            
            # Get the variable name
            if entity:
                var_name = f"{entity.get_variable_name()}.{self._sanitize_field_name(domain_field.field_name)}"
                if entity.cardinality == 'multiple':
                    var_name = f"{entity.get_variable_name()}[i].{self._sanitize_field_name(domain_field.field_name)}"
            else:
                var_name = self._sanitize_field_name(domain_field.field_name)
            
            # Create appropriate field based on type
            datatype = domain_field.get_docassemble_datatype()
            
            if datatype == DataType.CURRENCY:
                field_def = create_currency_field(
                    label=domain_field.field_label,
                    field_name=var_name,
                    required=domain_field.required,
                    help_text=domain_field.help_text
                )
            elif datatype == DataType.DATE:
                field_def = create_date_field(
                    label=domain_field.field_label,
                    field_name=var_name,
                    required=domain_field.required,
                    help_text=domain_field.help_text
                )
            elif datatype == DataType.YESNO:
                field_def = create_yesno_field(
                    label=domain_field.field_label,
                    field_name=var_name,
                    required=domain_field.required,
                    help_text=domain_field.help_text
                )
            elif datatype == DataType.COMBOBOX and domain_field.options:
                field_def = create_dropdown_field(
                    label=domain_field.field_label,
                    field_name=var_name,
                    choices=domain_field.options,
                    required=domain_field.required,
                    help_text=domain_field.help_text
                )
            else:
                field_def = create_text_field(
                    label=domain_field.field_label,
                    field_name=var_name,
                    required=domain_field.required,
                    help_text=domain_field.help_text
                )
            
            # Add validation if needed
            if domain_field.needs_validation():
                field_def.validate = self._get_validation_function(domain_field)
            
            field_defs.append(field_def)
            self.field_mappings[domain_field.field_id] = field_def
        
        return field_defs
    
    def create_entity_question(self, entity: DomainEntity, fields: List[DomainField]) -> Question:
        """Create a question for an entity with its fields"""
        entity_fields = [f for f in fields if f.entity_id == entity.entity_id]
        
        if not entity_fields:
            return None
        
        # Create field definitions
        field_defs = self.create_field_definitions(entity_fields, entity)
        
        # Generate question title
        title = self._get_entity_question_title(entity)
        
        # Create question
        question = Question(
            question=title,
            fields=field_defs
        )
        
        # Add special handling for lists
        if entity.cardinality == 'multiple':
            question.list_collect = True
        
        return question
    
    def _get_entity_question_title(self, entity: DomainEntity) -> str:
        """Generate appropriate question title for entity"""
        if entity.entity_type == 'person':
            if 'applicant' in entity.entity_name.lower():
                return "Applicant Information"
            elif 'respondent' in entity.entity_name.lower():
                return "Respondent Information"
            elif 'child' in entity.entity_name.lower():
                return "Child Information" if entity.cardinality == 'single' else "Children Information"
            else:
                return f"{entity.entity_name} Information"
        elif entity.entity_type == 'property':
            return f"{entity.entity_name} Details"
        elif entity.entity_type == 'financial':
            return f"{entity.entity_name}"
        else:
            return entity.entity_name
    
    def _sanitize_field_name(self, name: str) -> str:
        """Sanitize field name for Docassemble variable"""
        import re
        # Remove special characters and spaces
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_').lower()
        
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'field_' + name
        
        return name or "field"
    
    def _get_validation_function(self, field: DomainField) -> str:
        """Get validation function name for field type"""
        if field.field_type == 'sin':
            return 'validate_sin'
        elif field.field_type == 'email':
            return 'validate_email'
        elif field.field_type == 'phone':
            return 'validate_phone'
        elif field.field_type == 'postal_code':
            return 'validate_ontario_postal_code'
        else:
            return None
    
    def get_mandatory_flow(self, entities: List[DomainEntity]) -> List[str]:
        """Generate mandatory execution flow based on entities"""
        flow = ['intro_seen']
        
        # Add person entities first (in order)
        person_entities = [e for e in entities if e.entity_type == 'person']
        for entity in person_entities:
            var_name = entity.get_variable_name()
            if 'applicant' in var_name:
                flow.extend([
                    f'{var_name}.name.first',
                    f'{var_name}.name.last'
                ])
            elif 'respondent' in var_name:
                flow.extend([
                    f'{var_name}.name.first',
                    f'{var_name}.name.last'
                ])
        
        # Add list collections
        list_entities = [e for e in entities if e.cardinality == 'multiple']
        for entity in list_entities:
            var_name = entity.get_variable_name()
            flow.append(f'{var_name}.gathered')
        
        # Add data collection for single entities
        single_entities = [e for e in entities if e.cardinality == 'single' and e.entity_type != 'person']
        for entity in single_entities:
            flow.append(f'{entity.get_variable_name()}_complete')
        
        # Add standard completion steps
        flow.extend(['review_complete', 'form_complete'])
        
        return flow
    
    def export_mappings(self, output_file: str = "workflow_output/domain_mappings.json"):
        """Export all domain mappings to JSON"""
        mappings = {
            'entities': {},
            'fields': {},
            'object_declarations': {},
            'field_definitions': {}
        }
        
        # Export entities
        for entity_id, entity in self.entities.items():
            mappings['entities'][entity_id] = {
                'entity_type': entity.entity_type,
                'entity_name': entity.entity_name,
                'docassemble_type': entity.get_docassemble_type(),
                'variable_name': entity.get_variable_name(),
                'cardinality': entity.cardinality,
                'field_count': len(entity.field_ids)
            }
        
        # Export fields
        for field_id, domain_field in self.fields.items():
            mappings['fields'][field_id] = {
                'field_name': domain_field.field_name,
                'field_type': domain_field.field_type,
                'docassemble_datatype': domain_field.get_docassemble_datatype().value,
                'entity_id': domain_field.entity_id,
                'needs_validation': domain_field.needs_validation(),
                'required': domain_field.required
            }
        
        # Export object declarations
        for entity_id, obj_decl in self.object_mappings.items():
            mappings['object_declarations'][entity_id] = obj_decl.to_dict()
        
        # Export field definitions
        for field_id, field_def in self.field_mappings.items():
            mappings['field_definitions'][field_id] = field_def.to_dict()
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        logger.info(f"Exported domain mappings to {output_file}")
        return mappings


def test_domain_mapper():
    """Test the domain object mapper"""
    mapper = DomainObjectMapper()
    
    # Test with Form 13
    entities, fields = mapper.load_form_data("13")
    
    print(f"Loaded {len(entities)} entities and {len(fields)} fields for Form 13")
    
    # Create object declarations
    objects = mapper.create_object_declarations(entities)
    print(f"\nGenerated {len(objects)} object declarations:")
    for obj in objects[:5]:
        print(f"  - {obj.to_dict()}")
    
    # Create questions for entities
    print(f"\nGenerating questions for entities:")
    for entity in entities[:3]:
        question = mapper.create_entity_question(entity, fields)
        if question:
            print(f"  - {question.question}: {len(question.fields)} fields")
    
    # Generate mandatory flow
    flow = mapper.get_mandatory_flow(entities)
    print(f"\nMandatory flow ({len(flow)} steps):")
    for step in flow[:10]:
        print(f"  - {step}")
    
    # Export mappings
    mappings = mapper.export_mappings()
    print(f"\nExported mappings with {len(mappings['entities'])} entities and {len(mappings['fields'])} fields")


if __name__ == "__main__":
    test_domain_mapper()