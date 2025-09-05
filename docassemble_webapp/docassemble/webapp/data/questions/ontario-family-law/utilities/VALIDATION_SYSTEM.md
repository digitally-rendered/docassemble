# Field Validation, Deduplication, and Docassemble Mapping System

## Overview

This system ensures consistent field extraction across multiple parsers and automatically maps fields to docassemble objects.

## How It Works

### 1. Field Validation

The system validates fields across multiple parsers using:

- **Fuzzy Matching**: Fields with similar names/labels (>85% similarity) are grouped
- **Position Proximity**: Fields on the same or nearby pages are considered related
- **Type Consistency**: Fields must have the same type to be grouped
- **Consensus Building**: Higher confidence when multiple parsers agree

#### Validation Process:
```
Parser 1: "applicant_name" (confidence: 0.9)
Parser 2: "full_legal_name_applicant" (confidence: 0.85)
Parser 3: "Applicant Full Legal Name" (confidence: 0.8)
    ↓
Validated Field: "full_legal_name" (consensus: 0.95)
```

### 2. Field Deduplication

The system removes duplicate fields using:

- **Signature Generation**: Each field gets a unique signature based on type, name, and position
- **Similarity Calculation**: Weighted scoring (Type: 30%, Label: 50%, Position: 20%)
- **Threshold Matching**: Fields >90% similar are considered duplicates
- **Priority Selection**: Keeps the field with highest consensus score

#### Deduplication Example:
```
Before: 125 fields from all parsers
After:  59 unique fields (53% reduction)
```

### 3. Docassemble Object Mapping

The system automatically maps fields to appropriate docassemble objects:

#### Standard Mappings:

| Field Pattern | Docassemble Object | Path Example |
|--------------|-------------------|--------------|
| Applicant name/info | Individual | `users[0].name.first` |
| Respondent name/info | Individual | `users[1].name.first` |
| Child information | Individual | `children[i].name.first` |
| Address fields | Address | `users[i].address.city` |
| Financial amounts | Value | `users[i].income` |
| Dates | DAObject | `marriage.date` |
| Court info | DAObject | `court.file_number` |

#### Ontario-Specific Fields:

| Field | Validation Rule | Docassemble Mapping |
|-------|----------------|-------------------|
| Postal Code | `^[KLMNP]\d[A-Z]\s?\d[A-Z]\d$` | `address.postal_code` |
| SIN | `^\d{3}-\d{3}-\d{3}$` | `users[i].sin` (masked) |
| LSO Number | `^\d{5}[A-Z]?$` | `lawyers[i].lso_number` |
| Court File | `^[A-Z]{2}-\d{2}-\d{6}$` | `court.file_number` |

## Validation Metrics

### Consensus Scoring

```
Base Score = Average confidence across all parsers
+ Parser Bonus (5% per additional parser, max 20%)
+ Method Bonus (2% per extraction method, max 10%)
= Consensus Score (0.0 - 1.0)
```

### Quality Levels

- **High Confidence** (>0.8): Multiple parsers agree, high individual confidence
- **Medium Confidence** (0.5-0.8): Some parser agreement or single high-confidence parser
- **Low Confidence** (<0.5): Single parser, low confidence

## Usage

### Basic Validation Pipeline

```python
from field_validation_mapper import validate_and_map_fields

# Input: Results from multiple parsers
parser_results = {
    'parser1': [...fields...],
    'parser2': [...fields...],
    'parser3': [...fields...]
}

# Run validation pipeline
summary = validate_and_map_fields(parser_results)

# Output files:
# - validated_fields.json: Deduplicated, validated fields
# - validation_report.json: Detailed validation metrics
# - docassemble_structure.json: Ready-to-use YAML structure
```

### Advanced Usage

```python
from field_validation_mapper import (
    FieldValidator,
    FieldDeduplicator,
    DocassembleMapper
)

# Step 1: Validate
validator = FieldValidator()
validated_fields, report = validator.validate_fields(parser_results)

# Step 2: Deduplicate
deduplicator = FieldDeduplicator()
unique_fields = deduplicator.deduplicate(validated_fields)

# Step 3: Map to Docassemble
mapper = DocassembleMapper()
yaml_structure = mapper.generate_yaml_structure(unique_fields)
```

## Validation Report Structure

```json
{
  "total_validated_fields": 87,
  "multi_parser_fields": 18,
  "single_parser_fields": 69,
  "consensus_distribution": {
    "high": 23,
    "medium": 64,
    "low": 0
  },
  "parser_coverage": {
    "advanced_docx": {
      "total_fields": 20,
      "validated_fields": 20
    },
    "intelligent": {
      "total_fields": 105,
      "validated_fields": 67
    }
  },
  "docassemble_mappings": {
    "Individual": 5,
    "Address": 2,
    "Value": 47,
    "DAObject": 5
  }
}
```

## Benefits

1. **Consistency**: Ensures all parsers identify the same logical fields
2. **Accuracy**: Higher confidence through multi-parser validation
3. **Automation**: No manual field mapping required
4. **Deduplication**: Removes redundant fields automatically
5. **Ontario-Specific**: Built-in validation for Ontario legal requirements
6. **Docassemble-Ready**: Generates proper YAML structure immediately

## Validation Issues Detection

The system automatically detects and reports:

- Fields found by only one parser (potential misses)
- Low consensus scores (disagreement between parsers)
- Missing required fields
- Invalid field types
- Duplicate field mappings

## Performance

For Form 13 (Financial Statement):
- Input: 125 fields from 2 parsers
- Validated: 87 fields
- Deduplicated: 59 unique fields
- Multi-parser agreement: 18 fields (30%)
- Processing time: <1 second

## Integration with Workflow

```bash
# 1. Run parsers
python hybrid_form_parser.py form.docx

# 2. Validate and map
python field_validation_mapper.py

# 3. Generate YAML
python generate_docassemble_interview.py

# Result: Complete, validated docassemble interview
```