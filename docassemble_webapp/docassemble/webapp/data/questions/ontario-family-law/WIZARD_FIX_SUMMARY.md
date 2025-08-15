# Ontario Family Law Wizard - Validation Fix Summary

## Date: 2025-08-11

## Issues Fixed

### 1. Validation Syntax Errors
The wizard was using incorrect validation syntax throughout the file. The main issue was using `validate:` with lambda functions, which is not valid docassemble syntax.

#### Incorrect Syntax (Before):
```yaml
validate: |
  lambda x: True if condition else "Error message"
```

#### Correct Syntax (After):
```yaml
validation code: |
  if not condition:
    validation_error("Error message")
```

### 2. Specific Validations Fixed

All 9 validation blocks were corrected:

1. **Email validations (4 instances)**:
   - user_party.email (line 783-785)
   - other_party.email (line 860-862) 
   - user_lawyer.email (line 947-949)
   - other_lawyer.email (line 1024-1026)

2. **Postal code validations (4 instances)**:
   - user_party.address.postal_code (line 805-807)
   - other_party.address.postal_code (line 883-885)
   - user_lawyer.address.postal_code (line 969-971)
   - other_lawyer.address.postal_code (line 1046-1048)

3. **LSO number validation (1 instance)**:
   - other_lawyer.lso_number (line 994-996)

## Object Structure Maintained

As per requirements, the following object structure was preserved:

- **Parties**: Person objects (user_party, other_party, applicant, respondent)
- **Lawyers**: Individual objects (user_lawyer, other_lawyer)
- **Law Firms**: Organization objects (user_law_firm, other_law_firm)
- **Court**: DAObject with address sub-object

## Validation Patterns

The following regex patterns are used for validation:

1. **Email**: `r'^[\w\.\-]+@[\w\.\-]+\.\w+$'`
2. **Canadian Postal Code**: `r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$'`
3. **LSO Number**: `r'^\d{5}[A-Z]?$'`

## Test Files Created

Three test files were created to validate the fixes:

1. **test-wizard-validation.yml**: Simple include test to verify syntax
2. **test-wizard-flows.yml**: Tests different interview flows (emergency, never_together, etc.)
3. **test-wizard-complete.yml**: Comprehensive test of objects, validations, and patterns

## Key Points

- No functionality was removed - all validation logic was preserved
- All party collection flows remain intact (emergency, never-together, regular)
- Role-neutral party collection maintained
- All error handling and debug features retained
- The wizard should now load without syntax errors

## Next Steps

1. Run the test files to verify all validations work correctly
2. Test the main wizard with different scenarios
3. Verify that party information collection works for all flows
4. Ensure form recommendations are generated correctly