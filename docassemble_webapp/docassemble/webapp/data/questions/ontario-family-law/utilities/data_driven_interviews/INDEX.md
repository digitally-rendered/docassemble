# Data-Driven Form 13 Interviews

This directory contains Form 13 interviews generated using different approaches, all using parsed form data and domain mappings.

## Generated Interviews

### 1. Incremental Stages (in incremental_interviews/)
- **00_stage_index.yml** - Index page for all stages
- **form_13_stage_1_minimal.yml** - Bare minimum working interview
- **form_13_stage_2_structure.yml** - Basic structure with includes
- **form_13_stage_3_person.yml** - With Individual object
- **form_13_stage_4_financial.yml** - With financial fields
- **form_13_stage_5_errors.yml** - With error handling
- **form_13_stage_6_validation.yml** - With field validation  
- **form_13_stage_7_complete.yml** - Complete with domain mapping

### 2. Data-Driven Approaches (in data_driven_interviews/)

#### Simple Versions
- **form_13_simple.yml** - Simplified version without complex tables
- **form_13_working.yml** - Basic working version with clean structure

#### Incremental Data-Driven
- **form_13_step_4_simple.yml** - Simple version from parsed data
- **form_13_step_5_domains.yml** - With domain entity mapping

#### Full Data-Driven
- **form_13_data_driven.yml** - Original data-driven attempt
- **form_13_real_data.yml** - Uses actual Form 13 parsed income fields
- **form_13_structured.yml** - Built from Python data structures with error scaffolding

## Key Features

### Structured Data Generator (Recommended)
The `form_13_structured.yml` represents the best approach:
- Built from Python dictionaries/lists (not string templates)
- Includes error handling scaffolding (error_log, validation_errors)
- Uses domain mappings from workflow
- Safe value getters for currency fields
- Validation functions for data integrity
- Properly encoded to YAML

### Real Data Integration
All interviews use:
- Parsed fields from `workflow_output/enhanced_parsed_forms/form_13_fields.json`
- Domain mappings from `workflow_output/domain_mappings.json`
- Actual Form 13 income field indices (341-354)

## Testing

Test the interviews at these URLs:

**Incremental Stages:**
`/interview?i=docassemble.webapp:ontario-family-law/utilities/incremental_interviews/00_stage_index.yml`

**Structured (Recommended):**
`/interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_structured.yml`

**Real Data:**
`/interview?i=docassemble.webapp:ontario-family-law/utilities/data_driven_interviews/form_13_real_data.yml`

## Generator Scripts

- `incremental_generator.py` - Generates 7 progressive stages
- `incremental_data_driven_generator.py` - Shows data analysis steps
- `real_data_generator.py` - Uses actual parsed Form 13 fields
- `structured_data_generator.py` - Builds from Python data structures (recommended)

## Next Steps

1. Test each interview to verify they work
2. Apply the structured data approach to other forms
3. Add more sophisticated domain mapping
4. Implement table-based income/expense collection
5. Add PDF generation capability