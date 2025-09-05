# Ontario Family Law Forms - System Architecture

## Overview
A comprehensive system for parsing Ontario Family Law forms and generating structured Docassemble interviews with proper domain object mapping.

## Architecture Components

### 1. Domain Object Mapping System

#### `docassemble_interview_builder.py`
Provides structured Python APIs for building Docassemble components:
- **Data Classes**: `Metadata`, `Features`, `FieldDefinition`, `Question`, `ObjectDeclaration`, etc.
- **Builder Pattern**: `InterviewBuilder` class for composing interviews
- **Helper Functions**: Factory functions for common patterns
- **Type Safety**: Enums for data types, progress methods

Key Features:
```python
# Create structured components
metadata = Metadata(title="Form 13", form_number="13")
field = create_currency_field("Income", "applicant.income", required=True)
question = Question(question="Personal Info", fields=[field])
builder = InterviewBuilder()
builder.set_metadata(metadata).add_question(question)
yaml = builder.to_yaml()
```

#### `domain_object_mapper.py`
Maps detected form entities to Docassemble objects:
- **Entity Mapping**: Maps form entities (person, property, financial) to Docassemble types
- **Field Mapping**: Maps field types to appropriate Docassemble datatypes
- **Validation Rules**: Automatically applies Ontario-specific validation
- **Relationship Tracking**: Maintains entity-field relationships

Domain Mappings:
```python
Entity Type → Docassemble Object
'person' → 'Individual'
'property' → 'DAObject' 
'financial' → 'Income/Expense/Asset/Liability'
'address' → 'Address'
```

### 2. Interview Generation System

#### `structured_interview_generator.py`
Generates interviews using domain mappings and structured builders:
- Loads entities and fields from form analysis
- Creates appropriate Docassemble objects
- Generates entity-based questions
- Adds calculation functions for financial forms
- Includes proper validation and flow control

### 3. Data Flow

```
1. Form Analysis (form_relationship_analyzer.py)
   ↓
2. Domain Entity Detection
   - Person entities (applicant, respondent, children)
   - Property entities (real estate, vehicles, assets)
   - Financial entities (income, expenses, debts)
   ↓
3. Domain Object Mapping (domain_object_mapper.py)
   - Entity → Docassemble Object Type
   - Field → Docassemble DataType
   - Validation Rules
   ↓
4. Structured Interview Building (docassemble_interview_builder.py)
   - Metadata
   - Objects
   - Questions
   - Review Screens
   - Validation Code
   ↓
5. YAML Generation
   - Proper formatting
   - No string concatenation
   - Valid Docassemble syntax
```

## Generated Outputs

### Domain Mappings File
`workflow_output/domain_mappings.json`
- Complete entity-to-object mappings
- Field-to-datatype mappings
- Validation requirements
- Object declarations

### Structured Interviews
`workflow_output/structured_interviews/`
- 48 form interviews using structured components
- Proper domain object types
- Entity-based question organization
- Calculation functions

### Key Improvements Over String-Based Generation

1. **Type Safety**: Enums and data classes prevent invalid configurations
2. **Reusability**: Helper functions for common patterns
3. **Maintainability**: Clear separation of concerns
4. **Validation**: Built-in validation at the Python level
5. **Documentation**: Self-documenting through type hints

## Object Type Mappings

### Ontario Entity Types → Docassemble Objects

| Ontario Entity | Docassemble Object | Variable Name | Cardinality |
|---------------|-------------------|---------------|-------------|
| Applicant | Individual | applicant | Single |
| Respondent | Individual | respondent | Single |
| Children | Individual | children | List |
| Real Estate | DAObject | real_estates | List |
| Vehicle | DAObject | vehicles | List |
| Bank Account | DAObject | banks | List |
| Income Source | Income | income_sources | List |
| Expense Item | Expense | expenses | List |
| Debt | Liability | debts | List |
| Support Payment | DAObject | support_payments | List |

### Field Type Mappings

| Form Field Type | Docassemble DataType | Validation |
|-----------------|---------------------|------------|
| text | TEXT | - |
| currency | CURRENCY | min: 0 |
| date | DATE | - |
| email | EMAIL | validate_email |
| phone | TEXT | validate_phone |
| sin | TEXT | validate_sin |
| postal_code | TEXT | validate_ontario_postal_code |
| checkbox | YESNO | - |
| dropdown | COMBOBOX | - |

## Usage Examples

### Creating a Form Interview
```python
from structured_interview_generator import StructuredInterviewGenerator

generator = StructuredInterviewGenerator()
generator.generate_form_interview("13")  # Form 13
```

### Creating Custom Components
```python
from docassemble_interview_builder import *

# Create a person object
applicant = create_person_object("applicant", "Individual")

# Create a financial list
income = create_list_object("income_sources", "Income")

# Create a currency field
income_field = create_currency_field(
    "Annual Income", 
    "applicant.income",
    required=True,
    min_value=0
)

# Build interview
builder = InterviewBuilder()
builder.add_object(applicant)
builder.add_object(income)
builder.add_question(Question(
    question="Financial Information",
    fields=[income_field]
))
```

## Benefits

1. **Accuracy**: Domain entities properly mapped to correct Docassemble types
2. **Consistency**: All forms use same mapping rules
3. **Validation**: Ontario-specific validation automatically applied
4. **Calculations**: Financial forms get appropriate calculation functions
5. **Organization**: Questions grouped by entities
6. **Maintainability**: Changes to mappings apply to all forms

## Files Created

- `docassemble_interview_builder.py` - Structured component builder
- `domain_object_mapper.py` - Entity and field mapping system
- `structured_interview_generator.py` - Interview generator using mappings
- `workflow_output/domain_mappings.json` - Exported domain mappings
- `workflow_output/structured_interviews/` - 48 generated interviews

## Next Steps

1. Test generated interviews in Docassemble
2. Refine domain mappings based on testing
3. Add form-specific business logic
4. Implement cross-form data sharing
5. Add custom validation for specific Ontario requirements