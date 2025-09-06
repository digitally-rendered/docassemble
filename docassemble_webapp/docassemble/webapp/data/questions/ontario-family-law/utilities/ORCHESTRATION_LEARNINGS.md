# Ontario Family Law Forms Orchestration - Learnings & Best Practices

## Overview
This document captures the key learnings from building the Ontario Family Law forms automation system, including what worked, what didn't, and the final architecture.

## Key Learnings

### 1. Interview Architecture

#### ❌ What Didn't Work:
- **Including common fields in every form** - Creates massive redundancy
- **Direct YAML generation** - Generated invalid YAML with malformed field names
- **Monolithic interviews** - Too complex, hard to maintain
- **Field name parsing issues** - Original parsers created duplicate/malformed field names like `full_legal_name_full_legal_name_name_name`

#### ✅ What Works:
- **Separate common intake + form-specific interviews** - Clean separation of concerns
- **External orchestration** - Sequence interviews based on user needs
- **Python code that generates YAML** - More control and validation
- **Clean field mapping** - Proper variable naming and deduplication

### 2. Field Parsing & Processing

#### Problems Found:
```python
# Bad: Original parsed data
{
  "field_name": "full_legal_name_full_legal_name_name_name",
  "field_type": "date",  # Wrong type!
  "field_label": "Full legal name: Full legal name: Name: Name:"
}

# Good: Cleaned data
{
  "field_name": "applicant_name",
  "field_type": "text",
  "field_label": "Full legal name"
}
```

#### Solution:
- Clean labels by removing duplicates
- Generate proper variable names
- Correctly identify field types
- Map common fields to standard patterns

### 3. Common Interview Framework

The existing `common_intake_enhanced_with_validation.yml` provides:
- Emergency assessment
- MIP (Mandatory Information Program) check
- Party information (user, opposing_party)
- Lawyer information
- Court information
- Children information
- Basic financial assessment
- Orders being sought

**Key Insight:** Don't duplicate this - reference it!

### 4. Form-Specific Approach

Each form should only add its unique fields:

```yaml
# Form 8 specific additions (example)
---
include:
  - common_intake_enhanced_with_validation.yml
---
question: |
  Form 8 - Additional Claims Detail
fields:
  - Specific grounds for claim: form8_grounds
  - Previous court proceedings: form8_previous_proceedings
```

## Final Architecture

### 1. **Data Flow**
```
1. Parse Forms (existing parsers) 
   ↓
2. Clean & Categorize Fields (new)
   ↓
3. Identify Common vs Specific Fields
   ↓
4. Generate Form-Specific Interviews
   ↓
5. Generate Playwright Tests from YAML
   ↓
6. External Orchestration Sequences Interviews
```

### 2. **Interview Sequencing**
```python
# External orchestrator determines sequence
workflow = {
    "divorce_with_children": [
        "common_intake_enhanced_with_validation.yml",
        "form_8a_specific.yml",  # Divorce application
        "form_13_specific.yml",   # Financial statement
        "form_36_specific.yml",   # Affidavit for divorce
    ],
    "custody_only": [
        "common_intake_enhanced_with_validation.yml",
        "form_8_specific.yml",    # General application
    ]
}
```

### 3. **File Structure**
```
ontario-family-law/
├── common_intake_enhanced_with_validation.yml  # Base interview (DO NOT MODIFY)
├── form_specific_interviews/                   # Form-specific additions only
│   ├── form_8_specific.yml
│   ├── form_8a_specific.yml
│   └── ...
├── utilities/
│   ├── form_specific_generator.py             # Generates form-specific interviews
│   ├── yaml_to_playwright_generator.py        # Auto-generates tests
│   └── orchestration_engine.py                # Sequences interviews
└── playwright_tests/                          # Auto-generated tests
```

## Code Generators - Best Practices

### 1. **Field Cleaning**
```python
def clean_field_label(label: str) -> str:
    """Clean malformed labels from parsing"""
    # Remove duplicates
    parts = label.split(':')
    unique_parts = []
    seen = set()
    for part in parts:
        clean = part.strip()
        if clean and clean.lower() not in seen:
            unique_parts.append(clean)
            seen.add(clean.lower())
    
    return unique_parts[0] if unique_parts else label
```

### 2. **Variable Name Generation**
```python
def generate_variable_name(label: str, form_number: str) -> str:
    """Generate clean, unique variable names"""
    # Clean the label
    clean = re.sub(r'[^\w\s]', '', label.lower())
    clean = re.sub(r'\s+', '_', clean)
    
    # Remove duplicate words
    parts = clean.split('_')
    unique = []
    for part in parts:
        if part not in unique:
            unique.append(part)
    
    # Add form prefix for uniqueness
    return f"form{form_number}_{'_'.join(unique[:5])}"
```

### 3. **Common Field Detection**
```python
COMMON_PATTERNS = [
    r'applicant|petitioner',
    r'respondent',
    r'court.*file',
    r'children',
    # ... etc
]

def is_common_field(field_label: str) -> bool:
    """Check if field belongs in common intake"""
    for pattern in COMMON_PATTERNS:
        if re.search(pattern, field_label.lower()):
            return True
    return False
```

## Testing Strategy

### 1. **Auto-Generated Tests**
The `yaml_to_playwright_generator.py` creates tests by:
- Parsing YAML structure
- Extracting fields and flow
- Generating appropriate test data
- Creating validation tests

### 2. **Test Categories**
- **Happy Path**: Complete form with valid data
- **Field Validation**: Test each field type
- **Navigation**: Back button, progress bar
- **Edge Cases**: Timeout, refresh, mobile
- **Performance**: Load time benchmarks

## Orchestration Engine Requirements

### External Orchestrator Should:
1. **Determine user's legal situation** (divorce, custody, support, etc.)
2. **Select appropriate forms** based on situation
3. **Sequence interviews** in correct order
4. **Pass data between interviews** using Docassemble's session
5. **Track progress** across multiple forms
6. **Handle dependencies** (e.g., Form 13 required with Form 8)

### Example Orchestration Logic:
```python
class OntarioFormsOrchestrator:
    def determine_workflow(self, user_situation):
        if user_situation.get('seeking_divorce'):
            forms = ['8A', '36', '13']
            if user_situation.get('has_children'):
                forms.append('35.1')
        elif user_situation.get('seeking_support_only'):
            forms = ['8', '13']
        # ... etc
        
        return ['common_intake'] + [f'form_{n}_specific' for n in forms]
```

## Deployment Checklist

1. ✅ Common intake works and has tests
2. ✅ Form-specific generators create valid YAML
3. ✅ YAML-to-Playwright generator creates tests
4. ✅ Field parsing produces clean data
5. ⏳ External orchestrator sequences interviews
6. ⏳ Data passing between interviews
7. ⏳ PDF generation from completed interviews

## Next Steps

1. **Fix remaining parser issues** - Some forms still have malformed field data
2. **Build orchestration engine** - External system to sequence interviews
3. **Implement data passing** - Share session data between interviews
4. **Add PDF generation** - Map interview data to official PDF forms
5. **Create user dashboard** - Track progress across multiple forms

## Agent Updates Needed

Based on learnings, agents should be updated to:

1. **Always check for existing common patterns** before generating new code
2. **Generate form-specific additions only**, not complete interviews
3. **Use proper field cleaning** and variable naming
4. **Create tests from YAML** rather than hardcoding
5. **Consider orchestration** when designing multi-form workflows

## Summary

The key insight is that **separation of concerns** is critical:
- Common intake handles shared data
- Form-specific interviews add unique fields only
- External orchestration sequences everything
- Tests are generated from YAML structure
- Each component has a single responsibility

This modular approach is maintainable, testable, and scalable.