# Ontario Family Law Forms - Docassemble Implementation Plan

## 1. Priority List: Top 15 Most Commonly Used Forms

### Tier 1 - Essential Forms (Build First)
1. **Form 8** - Application (General) - The primary application form for most family court matters
2. **Form 10** - Answer - Response to applications
3. **Form 8A** - Application (Divorce) - Specific divorce application form
4. **Form 36** - Affidavit for Divorce - Required for uncontested divorce
5. **Form 13** - Financial Statement (Property and Support Claims) - Under $75,000 net family property
6. **Form 13.1** - Financial Statement (Property and Support Claims) - Over $75,000 net family property

### Tier 2 - High Priority Forms
7. **Form 14A** - Affidavit (General) - Most common affidavit form
8. **Form 17A** - Child Support Guidelines Table Look-up - Child support calculations
9. **Form 35.1** - Affidavit in Support of Claim for Custody or Access - Custody/access claims
10. **Form 6B** - Notice of Motion - For interim or procedural motions
11. **Form 13A** - Direction to Request or Redact Information - Privacy protection
12. **Form 14C** - Confirmation - Case conference confirmation

### Tier 3 - Important Supporting Forms
13. **Form 23** - Summons to Witness - For trial preparation
14. **Form 23A** - Summons to Witness Outside Ontario - Cross-jurisdictional matters
15. **Form 26C** - Statement of Issues - Trial preparation

## 2. Form Categories

### A. Divorce Proceedings
- Form 8A (Application - Divorce)
- Form 36 (Affidavit for Divorce)
- Form 25A (Divorce Order)
- Form 36B (Certificate of Divorce)

### B. General Applications & Responses
- Form 8 (Application - General)
- Form 10 (Answer)
- Form 14A (Affidavit - General)
- Form 6B (Notice of Motion)

### C. Financial Disclosure
- Form 13 (Financial Statement - Under $75K)
- Form 13.1 (Financial Statement - Over $75K)
- Form 13A (Direction to Request or Redact Information)

### D. Child-Related Matters
- Form 35.1 (Affidavit - Custody/Access)
- Form 17A (Child Support Guidelines Table)
- Form 8B (Application - Child Protection)
- Form 28A (Application - Adoption)

### E. Court Procedures & Case Management
- Form 14C (Confirmation)
- Form 17C (Conference Notice)
- Form 17D (Settlement Conference Brief)
- Form 23 (Summons to Witness)

### F. Enforcement
- Form 11 (Application - Contempt)
- Form 26 (Statement of Money Owed)
- Form 27 (Request for Financial Statement)

## 3. Form Dependencies

### Core Dependency Chains:
1. **Divorce Process**:
   - Form 8A (Application) → Form 36 (Affidavit for Divorce) → Form 25A (Divorce Order)
   - Often requires Form 13/13.1 (Financial Statement) if support/property claims

2. **General Family Matters**:
   - Form 8 (Application) → Form 10 (Answer) → Form 14A (Affidavit)
   - Form 13/13.1 typically required for support/property claims

3. **Motion Proceedings**:
   - Form 6B (Notice of Motion) → Form 14A (Affidavit) → Form 14C (Confirmation)

4. **Case Management**:
   - Most applications → Form 14C (Confirmation) for case conferences
   - Form 17C (Conference Notice) → Form 17D (Settlement Conference Brief)

### Common Supporting Documents:
- Form 13A (Privacy direction) often accompanies financial forms
- Form 35.1 required for any custody/access claims
- Form 17A integrated into support calculations

## 4. Common Data Elements

### A. Party Information (Appears in 90%+ of forms)
- Full legal names (including maiden names)
- Current addresses (service address vs. residential)
- Phone numbers, email addresses
- Date of birth
- Occupation and employer information
- Lawyer information (if represented)

### B. Case Information
- Court file number
- Court office location
- Case type/nature of application
- Previous court orders or case numbers
- Related proceedings

### C. Relationship Information
- Date of marriage/cohabitation
- Date of separation
- Children information (names, DOB, current residence)
- Previous relationships affecting support obligations

### D. Financial Information
- Employment details and income
- Assets and liabilities
- Monthly expenses
- Support obligations to others
- Previous court orders for support

### E. Child-Related Information
- Children's names, dates of birth
- Current living arrangements
- School and healthcare information
- Special needs or circumstances
- Existing custody/access arrangements

## 5. Implementation Order

### Phase 1: Foundation Forms (Months 1-2)
1. **Form 8** (Application - General) - Establishes core party/case structure
2. **Form 13** (Financial Statement - Under $75K) - Most common financial form
3. **Form 14A** (Affidavit - General) - Basic affidavit template

### Phase 2: Core Divorce Forms (Month 3)
4. **Form 8A** (Application - Divorce) - Builds on Form 8 structure
5. **Form 36** (Affidavit for Divorce) - Completes basic divorce package

### Phase 3: Response and Motion Forms (Month 4)
6. **Form 10** (Answer) - Response capability
7. **Form 6B** (Notice of Motion) - Motion procedures

### Phase 4: Advanced Financial and Child Forms (Month 5)
8. **Form 13.1** (Financial Statement - Over $75K) - Builds on Form 13
9. **Form 35.1** (Affidavit - Custody/Access) - Child-related matters
10. **Form 17A** (Child Support Guidelines) - Support calculations

### Phase 5: Case Management and Procedural Forms (Month 6)
11. **Form 14C** (Confirmation)
12. **Form 13A** (Privacy Direction)
13. **Form 23** (Summons to Witness)

### Phase 6: Specialized Forms (Months 7-8)
14. Remaining forms based on user feedback and usage statistics

## 6. Ontario-Specific Requirements

### A. Court Rules Compliance
- **Ontario Family Law Rules** govern all forms and procedures
- Forms must include mandatory disclaimers about legal advice
- Specific formatting requirements for court filings
- Signature requirements and commissioner for oaths provisions

### B. Validation Rules
- **Court File Number Format**: Validation for proper format (e.g., FS-23-123456-00)
- **Postal Code Validation**: Canadian postal code format (A1A 1A1)
- **SIN Validation**: Social Insurance Number format and check digit
- **Date Validations**: Canadian date format (DD/MM/YYYY or DD-MMM-YYYY)

### C. Privacy and Confidentiality
- **Form 13A Integration**: Automatic privacy direction prompts
- **Sealing Requirements**: Certain information must be sealed from public access
- **Children's Information Protection**: Special handling of children's personal details

### D. Filing and Service Requirements
- **Original vs. Copy Requirements**: Different signature requirements
- **Service Methods**: Personal service, alternative service, substituted service
- **Filing Deadlines**: Form-specific timing requirements
- **Fee Calculations**: Court filing fees by form type

### E. Language and Accessibility
- **Official Languages**: Forms available in English and French
- **Plain Language Requirements**: Forms must be understandable
- **Accessibility Standards**: AODA compliance for digital forms

### F. Integration Requirements
- **Justice Services Online (JSO)**: Electronic filing capabilities
- **Child Support Guidelines**: Automated calculations
- **Court Scheduling**: Integration with case management conferences
- **CRA Integration**: Income verification where permitted

### G. Quality Assurance
- **Legal Review Process**: All forms require legal professional review
- **User Testing**: Forms tested with self-represented litigants
- **Court Feedback**: Regular feedback from court staff and judiciary
- **Version Control**: Tracking form updates and rule changes

## Technical Considerations for Docassemble Implementation

### A. Shared Components
- Common party information collection module
- Financial information gathering template
- Children information collection module
- Court and case information template
- Document assembly and formatting engine

### B. Data Validation
- Real-time validation for required fields
- Format checking for numbers, dates, postal codes
- Cross-field validation (e.g., separation date after marriage date)
- Completeness checking before form generation

### C. User Experience
- Progressive disclosure of complex sections
- Help text and examples for difficult concepts
- Conditional logic to show/hide irrelevant sections
- Save and resume functionality for complex forms

### D. Output Generation
- PDF generation matching official court formats
- Multiple output formats (fillable PDF, court-ready PDF)
- Email delivery and secure document storage
- Print-friendly versions

This implementation plan provides a structured approach to building a comprehensive Ontario family law automation system that prioritizes the most commonly used forms while ensuring legal compliance and user accessibility.