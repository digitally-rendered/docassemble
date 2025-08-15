# Ontario Family Law Financial Statement Forms

Comprehensive Docassemble implementation of Ontario Court Forms 13 and 13.1 - Financial Statements for family law proceedings.

## Overview

This implementation provides sophisticated financial disclosure forms required in Ontario family law cases involving support and property matters. The system automatically routes users to the appropriate form based on income thresholds and financial complexity.

## Forms Included

### Form 13 - Complex Financial Statement
**File:** `form-13-financial-statement.yml`
- **Purpose:** For income over $150,000 or complex financial situations
- **Features:**
  - Comprehensive income tracking (employment, business, investment, other)
  - Detailed expense categorization
  - Asset valuation with professional valuation requirements
  - Business interest disclosure and valuation
  - Investment portfolio tracking
  - Professional practice valuations
  - Child support calculations with special expenses
  - Complete document generation with attachments

### Form 13.1 - Simple Financial Statement  
**File:** `form-13-1-financial-statement-simple.yml`
- **Purpose:** For income under $150,000 with straightforward finances
- **Features:**
  - Streamlined income reporting
  - Essential expense categories
  - Basic asset and debt tracking
  - Simplified child support calculations
  - Faster completion process
  - User-friendly interface for self-represented litigants

### Financial Statement Selector
**File:** `financial-statement-selector.yml`
- **Purpose:** Interactive tool to help users choose the correct form
- **Features:**
  - Income threshold assessment
  - Financial complexity evaluation
  - Business and investment analysis
  - Form recommendation with detailed explanations
  - Professional advice routing

## Technical Architecture

### Core Components

#### 1. Calculation Modules

**Child Support Calculator** (`child_support_calculator.py`)
- Federal Child Support Guidelines implementation
- Table amount calculations for Ontario
- Special expenses sharing calculations
- Income validation and assessment
- Integration with official guidelines

**Business Valuation Helper** (`business_valuation_helpers.py`)
- Professional valuation requirement assessment
- Business cash flow calculations
- Valuation method recommendations
- Cost and timeframe estimates
- Professional valuator directory integration

**Simple Financial Calculator** (`simple_financial_calculators.py`)
- Basic financial calculations for Form 13.1
- Net worth and surplus/deficit calculations
- Expense reasonableness assessment
- Debt service ratio analysis
- Form 13.1 eligibility validation

#### 2. Shared Components

**Common Components** (`ontario-family-law-common.yml`)
- Validation functions (postal codes, phone numbers, SIN)
- Court location data
- Common data objects and templates
- Privacy protection functions
- Document generation helpers

### Key Features

#### Financial Calculations
- **Automatic Calculations:** Real-time calculation of totals, percentages, and ratios
- **Validation:** Comprehensive input validation with contextual error messages
- **Child Support:** Integration with Federal Child Support Guidelines
- **Professional Valuations:** Automated assessment of valuation requirements

#### User Experience
- **Smart Routing:** Automatic form selection based on user responses
- **Progressive Disclosure:** Complex information gathered in logical steps
- **Help Text:** Comprehensive explanations and examples
- **Review Screens:** Complete review before submission
- **Error Handling:** Clear validation messages and correction guidance

#### Legal Compliance
- **Privacy Protection:** Multiple levels of privacy safeguards
- **Professional Standards:** Built-in recommendations for professional review
- **Court Requirements:** Compliance with Ontario Family Law Rules
- **Documentation:** Complete supporting document checklists

#### Security & Privacy
- **Data Encryption:** Secure handling of sensitive financial information
- **Privacy Notices:** Clear disclosure of information use and sharing
- **Access Controls:** Appropriate access restrictions
- **Audit Trail:** Logging of data access and modifications

## Usage

### Form Selection Process

1. **Initial Assessment**
   - User provides basic financial information
   - System evaluates income threshold ($150,000)
   - Assessment of financial complexity factors

2. **Smart Routing**
   - Automatic recommendation of appropriate form
   - Clear explanation of differences
   - Option to override recommendation with warnings

3. **Form Completion**
   - Progressive data collection
   - Real-time validation and calculations
   - Professional valuation assessment
   - Document generation

### Form 13 (Complex) Workflow

1. **Eligibility Confirmation**
   - Income threshold verification
   - Complexity assessment
   - Professional valuation requirements

2. **Comprehensive Data Collection**
   - Detailed income from all sources
   - Complete expense categorization  
   - Asset inventory with valuations
   - Business interest disclosure
   - Investment portfolio details

3. **Professional Requirements**
   - Automatic assessment of valuation needs
   - Cost and timeframe estimates
   - Professional directory integration

4. **Final Review and Generation**
   - Complete financial summary
   - Document package generation
   - Supporting document checklist

### Form 13.1 (Simple) Workflow

1. **Eligibility Verification**
   - Income threshold confirmation
   - Simplicity assessment
   - Redirect to Form 13 if needed

2. **Streamlined Data Collection**
   - Basic income sources
   - Essential expense categories
   - Simple asset and debt inventory
   - Children information

3. **Quick Calculations**
   - Basic child support estimates
   - Net worth calculation
   - Surplus/deficit analysis

4. **Document Generation**
   - Simple financial statement
   - Basic document checklist

## Supporting Documentation

### Required Documents (Form 13)
- Tax returns and Notices of Assessment (3 years)
- Employment letters and pay stubs
- Business financial statements and tax returns
- Professional valuations for significant assets
- Investment account statements
- Bank statements for all accounts
- Property assessments and mortgage statements
- Detailed expense documentation

### Required Documents (Form 13.1)
- Most recent tax return and Notice of Assessment
- Current pay stubs or employment letter
- Bank statements (recent)
- Basic expense documentation
- Children's birth certificates
- Childcare receipts (if applicable)

## Professional Integration

### Legal Professionals
- **Review Templates:** Structured formats for lawyer/paralegal review
- **Professional Notes:** Fields for professional commentary
- **Court Filing:** Ready-to-file document packages
- **Service Requirements:** Automatic service instruction generation

### Financial Professionals
- **Accountant Review:** Structured financial summaries
- **Business Valuations:** Professional valuator integration
- **Tax Implications:** Built-in tax consideration prompts
- **Financial Planning:** Integration with financial planning tools

### Court System
- **Filing Requirements:** Compliance with court filing standards
- **Fee Calculations:** Automatic filing fee determination
- **Service Rules:** Integration with Family Law Rules requirements
- **Document Standards:** Court-compliant document formatting

## Quality Assurance

### Testing
- **Unit Tests:** Comprehensive test suite for all calculation modules
- **Integration Tests:** End-to-end form completion testing
- **Validation Tests:** Input validation and error handling
- **Calculation Tests:** Financial calculation accuracy verification

### Validation
- **Legal Review:** Forms reviewed by Ontario family law practitioners
- **Technical Review:** Code review by experienced developers
- **User Testing:** Usability testing with target users
- **Compliance Check:** Verification of court rule compliance

## Installation and Configuration

### Prerequisites
- Docassemble server environment
- Python 3.7+ with decimal and datetime modules
- Access to Ontario court filing systems (optional)
- Professional valuator directory integration (optional)

### Installation Steps
1. Copy all YAML files to the Docassemble questions directory
2. Install Python calculation modules
3. Configure court location data
4. Set up professional directory integrations
5. Test forms with sample data

### Configuration Options
- **Court Locations:** Update court directory for specific regions
- **Professional Networks:** Configure valuator and legal directories
- **Filing Fees:** Update fee schedules as required
- **Guidelines:** Update child support guideline tables
- **Privacy Settings:** Configure privacy protection levels

## Maintenance

### Regular Updates
- **Child Support Guidelines:** Annual updates to table amounts
- **Court Fees:** Updates to filing fee schedules
- **Professional Directories:** Updates to professional listings
- **Legal Requirements:** Updates to Family Law Rules compliance

### Monitoring
- **Usage Analytics:** Track form completion rates and user paths
- **Error Monitoring:** Monitor validation errors and user issues
- **Performance:** Track calculation performance and response times
- **User Feedback:** Collect and analyze user experience feedback

## Support and Resources

### For Users
- **Help Documentation:** Comprehensive user guides
- **Video Tutorials:** Step-by-step completion guidance
- **FAQ:** Common questions and answers
- **Professional Directory:** Access to legal and financial professionals

### For Developers
- **API Documentation:** Complete API reference
- **Code Examples:** Sample implementations and integrations
- **Testing Framework:** Test data and validation procedures
- **Deployment Guide:** Production deployment instructions

### For Legal Professionals
- **Training Materials:** Professional development resources
- **Integration Guides:** Law firm system integration
- **Review Checklists:** Quality assurance procedures
- **Compliance Updates:** Ongoing legal requirement updates

## Version History

### Version 1.0.0 (2025-08-09)
- Initial implementation
- Complete Form 13 and Form 13.1
- Smart routing and form selection
- Comprehensive calculation modules
- Professional valuation integration
- Privacy protection implementation
- Document generation and checklists
- Test suite and quality assurance

## License and Legal

This implementation is designed for use with the Ontario family law system and complies with applicable privacy legislation and court rules. Users are responsible for ensuring compliance with current legal requirements and obtaining appropriate professional advice.

**Important:** This system provides form completion assistance but does not constitute legal advice. Users should consult with qualified legal professionals for advice on their specific circumstances.

## Contact and Support

For technical issues, feature requests, or legal compliance questions, please contact the Ontario Family Law Forms Development Team.

**Remember:** These forms deal with sensitive financial information and legal obligations. Professional review is recommended, especially for complex financial situations.