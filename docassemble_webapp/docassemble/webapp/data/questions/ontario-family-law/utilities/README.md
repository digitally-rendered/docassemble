# Docassemble Word Document Analysis Utilities

These utilities provide form field extraction from Word documents, addressing the non-functional form field detection in docassemble Admin.

## Scripts

### 1. download_all_forms.py
Comprehensive downloader for all Ontario Family Law forms from ontariocourtforms.on.ca.

**Features:**
- Downloads 48+ core Ontario family law forms
- Organizes forms by category (applications, financial, motions, etc.)
- Creates an index file with all form details
- Respectful downloading with delays
- Resume capability and error handling

**Usage:**
```bash
python download_all_forms.py [download_directory]
```

**Output:** Forms organized in categorized folders:
- `core_applications/` - Form 8, 8A, 10, etc.
- `financial_statements/` - Form 13, 13.1, 13A, etc.  
- `motions_conferences/` - Form 14B, 15, 17A, etc.
- `orders/` - Form 25, 25A, 25C, etc.
- `enforcement/` - Form 26, 27, 28, 29, etc.
- `divorce_specific/` - Form 36, 36A
- `child_protection_adoption/` - Form 33F, 34, 34A, etc.
- `interjurisdictional/` - Form 37, 37A, 37B
- `alternative_dispute/` - Form 43, 43A, 43B

### 2. extract_form_fields.py
Extracts and categorizes form fields from Word documents, specifically optimized for Ontario Family Court forms.

**Usage:**
```bash
python extract_form_fields.py [path/to/document.docx]
```

**Output:** Categorized list of form fields organized by:
- Court Information
- Party Information  
- Date Fields
- Marriage Information
- Children Information
- Legal Claims
- Other Fields

### 2. analyze_word_doc.py
Comprehensive Word document structure analysis for docassemble integration planning.

**Usage:**
```bash
python analyze_word_doc.py [path/to/document.docx]
```

**Output:** Detailed document analysis including:
- Paragraph count and content
- Table structure and potential form fields
- Content controls detection
- Summary statistics

## Requirements

```bash
pip install python-docx
```

## Example Usage

```bash
# Analyze the Ontario Form 8
python extract_form_fields.py /path/to/flr-8-jun25-en.docx

# Detailed analysis of any Word document
python analyze_word_doc.py /path/to/any-form.docx
```

## Integration with Docassemble

These utilities help bridge the gap between Word forms and docassemble interviews by:

1. Identifying all form fields that need to be collected
2. Categorizing fields for logical interview flow
3. Providing field names for docassemble variable mapping
4. Understanding document structure for template creation

The extracted field information can be used to:
- Create docassemble interview questions
- Map variables to Word template placeholders
- Design interview logic flow
- Generate comprehensive form coverage

## Notes

- These utilities work with standard Word (.docx) format
- Optimized for Ontario Family Court forms but adaptable to other forms
- Provides alternative to broken docassemble Admin form field detection
- Field categorization can be customized by modifying the `field_patterns` dictionary