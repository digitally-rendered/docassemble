# Enhanced Ontario Family Law Form Generator

## Overview

This is a comprehensive Python code system that **programmatically generates Docassemble interviews** for Ontario family law forms using YAML objects and dataclasses. The system integrates with existing parsing infrastructure while replacing problematic generation approaches with clean, reusable components.

## Architecture

### ✅ **Existing Infrastructure (Preserved)**
- `automated_form_processor.py` - Form processing workflow 
- `field_validation_mapper.py` - Field validation and mapping
- `comprehensive_form_parser.py` - PDF/DOCX parsing with Google Cloud
- `parsed_forms/` directory - All parsed JSON field data (26+ forms)
- `ontario_forms_registry.json` - Form metadata registry

### 🆕 **New Generation System (Added)**
- `ontario_common_fields.py` - Common field definitions & validation
- `ontario_party_objects.py` - Person/organization dataclasses  
- `ontario_court_objects.py` - Court and case information objects
- `ontario_children_objects.py` - Children and family structure objects
- `ontario_financial_objects.py` - Financial statement components
- `common_interview_generator.py` - Main code generation engine
- `enhanced_form_integration.py` - Integration orchestrator
- `run_enhanced_generation.py` - Main executable

## Key Features

### 🎯 **YAML Object Generation**
- Creates YAML using proper `yaml.dump()` encoding
- No string concatenation or manual YAML construction
- Clean dataclass-to-YAML conversion

### ♻️ **Component Reusability** 
- Common field patterns shared across all forms
- Standardized party, court, children, and financial components
- Consistent validation and error handling

### 🔗 **Integration Approach**
- **Keeps**: All existing parsing infrastructure and data
- **Replaces**: Only the problematic YAML generation parts
- **Enhances**: Adds common components and better structure

### 📊 **Form Coverage**
Supports all major Ontario family law forms:
- **Form 8** - Application (General)
- **Form 8A** - Application (Divorce)  
- **Form 10** - Answer
- **Form 13** - Financial Statement (Support)
- **Form 13.1** - Financial Statement (Property)
- **Form 15** - Motion to Change
- **Form 36** - Affidavit for Divorce
- And 20+ additional forms with parsed data

## Usage

### Quick Start

```bash
# Show system demonstration
python run_enhanced_generation.py --demo

# Generate sample interview  
python run_enhanced_generation.py --sample

# Generate specific form
python run_enhanced_generation.py --form 8

# Generate all forms
python run_enhanced_generation.py --all

# Show generated files
python run_enhanced_generation.py --files
```

### Programmatic Usage

```python
from common_interview_generator import CommonInterviewGenerator
from enhanced_form_integration import EnhancedFormIntegrator

# Generate base interview with common components
generator = CommonInterviewGenerator()
interview = generator.generate_interview("8")  # Form 8
yaml_content = interview.to_yaml()

# Generate enhanced interview with existing parsed data
integrator = EnhancedFormIntegrator()
result = integrator.generate_enhanced_interview("8")
print(f"Generated: {result.generated_file_path}")
```

## Component Details

### 1. Common Fields (`ontario_common_fields.py`)

Provides standardized field definitions with validation:

```python
from ontario_common_fields import ontario_common_fields

# Get party-related fields
party_fields = ontario_common_fields.get_fields_by_category("party")

# Generate validation functions
validation_code = ontario_common_fields.generate_validation_functions()

# Create YAML field objects
field_objects = ontario_common_fields.generate_fields_yaml_objects(
    ["applicant_full_name", "respondent_full_name"]
)
```

### 2. Party Objects (`ontario_party_objects.py`)

Handles person and lawyer information:

```python
from ontario_party_objects import ontario_party_generator

# Generate party objects for Docassemble
objects = ontario_party_generator.generate_party_objects()

# Generate party questions
questions = ontario_party_generator.generate_party_questions("applicant")

# Generate complete party interview
interview = ontario_party_generator.generate_complete_party_interview("8")
```

### 3. Court Objects (`ontario_court_objects.py`)

Manages court and case information:

```python
from ontario_court_objects import ontario_court_generator

# Generate court questions
questions = ontario_court_generator.generate_court_questions()

# Get specific court information
court = ontario_court_generator.get_court_by_location("toronto")

# Generate validation code
validation = ontario_court_generator.generate_court_validation_code()
```

### 4. Children Objects (`ontario_children_objects.py`)

Handles children and family structure:

```python
from ontario_children_objects import ontario_children_generator

# Generate children questions
questions = ontario_children_generator.generate_children_questions()

# Estimate child support
support = ontario_children_generator.estimate_child_support(
    payor_income=75000, 
    children_count=2
)

# Generate complete children interview
interview = ontario_children_generator.generate_complete_children_interview("8")
```

### 5. Financial Objects (`ontario_financial_objects.py`)

Manages Form 13 financial statements:

```python
from ontario_financial_objects import ontario_financial_generator

# Generate income questions
income_questions = ontario_financial_generator.generate_income_questions()

# Generate complete financial statement
financial_interview = ontario_financial_generator.generate_complete_financial_interview()

# Generate simplified financial questions
simple_questions = ontario_financial_generator.generate_simplified_financial_questions()
```

### 6. Main Generator (`common_interview_generator.py`)

Orchestrates all components:

```python
from common_interview_generator import CommonInterviewGenerator

generator = CommonInterviewGenerator()

# Generate complete interview for any form
interview = generator.generate_interview("8")

# Generate all configured interviews
generated_files = generator.generate_all_common_interviews()

# Integration with parsed data
interview_with_data = generator.generate_integration_with_parsed_data(
    "8", "parsed_forms/form_8_fields.json"
)
```

## Generated Interview Structure

Each generated interview includes:

1. **Metadata** - Title, version, author, tags
2. **Includes** - Shared YAML files for common components
3. **Objects** - Docassemble object definitions
4. **Mandatory Logic** - Interview flow control
5. **Question Sections**:
   - Introduction
   - Party information
   - Court information  
   - Marriage information (if applicable)
   - Children information (if applicable)
   - Financial information (if applicable)
   - Form-specific questions
   - Review and document assembly
6. **Validation Code** - Ontario-specific validation functions

## Integration with Existing System

### Data Flow

```
Existing Parsed Data → Field Validation → Common Components → Enhanced Interview
     ↓                      ↓                   ↓                    ↓
parsed_forms/*.json → ValidatedField → YAML Objects → Complete Interview
```

### Preservation Strategy

- **Keeps all existing parsing work** - No re-parsing required
- **Reuses all ValidatedField objects** - Maintains validation scores
- **Preserves FormConfiguration** - Uses existing form metadata
- **Integrates with AutomatedFormProcessor** - Maintains workflow

## Ontario-Specific Features

### Court Information
- All Ontario Superior Court locations
- Court file number validation
- Case type determination

### Legal Requirements  
- Ontario postal code validation
- Canadian phone number validation
- SIN number validation (with Luhn algorithm)
- Ontario-specific field patterns

### Family Law Components
- Child support calculation estimates
- Custody arrangement templates  
- Financial statement components (Form 13/13.1)
- Marriage and separation information

## Output Files

Generated files are saved to `generated_interviews/`:
- `form_8_enhanced.yml` - Form 8 interview
- `form_13_enhanced.yml` - Form 13 interview
- `form_15_enhanced.yml` - Form 15 interview
- `processing_report.txt` - Generation report
- Additional forms as available

## Error Handling and Validation

### Built-in Validations
- Required field checking
- Data type validation (dates, currency, email)
- Ontario-specific format validation
- Cross-field logical validation

### Error Recovery
- Graceful handling of missing parsed data
- Fallback to base interview structure
- Comprehensive logging and reporting

## Performance and Scalability

### Efficiency Features
- Component caching and reuse
- Incremental field processing
- Optimized YAML generation
- Memory-efficient dataclass usage

### Scalability
- Easily add new forms
- Extend common components
- Add new field types and validations
- Support additional provinces/jurisdictions

## Testing and Quality Assurance

### Validation Scores
- Field consensus scoring from multiple parsers
- Interview completeness metrics
- Generation success tracking

### Quality Metrics
- Processing time monitoring
- Field count validation
- YAML syntax verification
- Component integration testing

## Future Enhancements

### Planned Features
- Additional form types (enforcement, adoption)
- Multi-language support
- Enhanced financial calculations
- Court rule integration

### Extension Points
- Custom field types
- Additional validation patterns
- Integration with external APIs
- Enhanced document generation

## Support and Documentation

### Getting Help
- Check `enhanced_generation.log` for processing details
- Review `processing_report.txt` for generation summary
- Use `--demo` mode to understand components
- Enable debug logging for troubleshooting

### Contributing
- Add new common field patterns in `ontario_common_fields.py`
- Extend form configurations in `common_interview_generator.py`
- Add validation functions to component files
- Update documentation for new features

## License and Legal

This tool generates form completion interviews but does not provide legal advice. Users should consult with qualified legal professionals for legal guidance. Generated forms must still comply with current Ontario Family Law Rules and court requirements.

---

**Generated by:** SettleWise Enhanced Form Generator  
**Version:** 2.0  
**Updated:** 2025-01-05