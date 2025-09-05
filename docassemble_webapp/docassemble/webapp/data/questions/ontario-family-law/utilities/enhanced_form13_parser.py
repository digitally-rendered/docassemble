#!/usr/bin/env python3
"""
Enhanced Form 13 Parser - Captures ALL financial tables and document requirements
Detects income, expenses, assets, debts, and prompts for supporting documents
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialTable:
    """Represents a financial table in Form 13"""
    table_type: str  # income, expense, asset, debt, etc.
    table_name: str
    table_id: str
    page_number: int
    
    # Table structure
    columns: List[Dict] = field(default_factory=list)
    rows: List[Dict] = field(default_factory=list)
    
    # Special fields for assets/debts
    requires_value: bool = False
    requires_statements: bool = False
    statement_frequency: str = ""  # monthly, quarterly, annual
    
    # Document requirements
    required_documents: List[str] = field(default_factory=list)
    optional_documents: List[str] = field(default_factory=list)

@dataclass
class DocumentRequirement:
    """Represents a document upload requirement"""
    doc_type: str  # statement, tax_return, noa, receipt, etc.
    doc_name: str
    related_field: str
    frequency: str  # one-time, monthly, quarterly, annual
    years_required: int = 1
    required: bool = True
    description: str = ""
    accepted_formats: List[str] = field(default_factory=lambda: ["pdf", "jpg", "png"])

class EnhancedForm13Parser:
    """
    Enhanced parser specifically for Form 13 Financial Statement
    Captures all tables and document requirements
    """
    
    # Form 13 specific table patterns
    INCOME_TABLES = {
        "employment_income": {
            "patterns": ["Employment income", "Salary", "wages", "commissions"],
            "requires_docs": ["pay stubs", "T4", "employment letter"]
        },
        "self_employment": {
            "patterns": ["Self-employment", "business income", "professional income"],
            "requires_docs": ["T2125", "financial statements", "bank statements"]
        },
        "investment_income": {
            "patterns": ["Investment", "dividends", "interest", "capital gains"],
            "requires_docs": ["T5", "T3", "investment statements"]
        },
        "rental_income": {
            "patterns": ["Rental income", "rent received"],
            "requires_docs": ["lease agreements", "T776", "rental statements"]
        },
        "support_income": {
            "patterns": ["Support", "spousal support", "child support"],
            "requires_docs": ["support orders", "payment records"]
        },
        "government_benefits": {
            "patterns": ["EI", "CPP", "OAS", "Child Tax", "GST", "Ontario Works"],
            "requires_docs": ["benefit statements", "T4E", "T4A"]
        }
    }
    
    EXPENSE_TABLES = {
        "housing": {
            "patterns": ["Housing", "Rent", "Mortgage", "Property tax", "Utilities"],
            "requires_docs": ["lease", "mortgage statement", "utility bills", "property tax bill"]
        },
        "transportation": {
            "patterns": ["Transportation", "Car payment", "Insurance", "Gas", "Transit"],
            "requires_docs": ["loan agreement", "insurance policy", "gas receipts"]
        },
        "childcare": {
            "patterns": ["Child care", "Daycare", "After school", "Summer camp"],
            "requires_docs": ["childcare receipts", "provider statements"]
        },
        "medical": {
            "patterns": ["Medical", "Health", "Dental", "Prescription", "Therapy"],
            "requires_docs": ["receipts", "insurance statements", "prescription records"]
        },
        "debt_payments": {
            "patterns": ["Debt", "Credit card", "Line of credit", "Loan payment"],
            "requires_docs": ["statements", "loan agreements"]
        }
    }
    
    ASSET_TABLES = {
        "real_estate": {
            "patterns": ["Real Estate", "Property", "Land", "Home", "Cottage"],
            "requires_docs": ["deed", "mortgage statement", "property assessment", "MPAC"],
            "requires_value": True
        },
        "vehicles": {
            "patterns": ["Vehicle", "Car", "Motorcycle", "Boat", "RV"],
            "requires_docs": ["ownership", "loan statement", "valuation"],
            "requires_value": True
        },
        "bank_accounts": {
            "patterns": ["Bank account", "Chequing", "Savings", "Joint account"],
            "requires_docs": ["bank statements (12 months)", "account verification"],
            "requires_value": True,
            "statement_frequency": "monthly"
        },
        "investments": {
            "patterns": ["Investment", "RRSP", "TFSA", "Stocks", "Bonds", "GIC"],
            "requires_docs": ["statements", "portfolio summary"],
            "requires_value": True,
            "statement_frequency": "quarterly"
        },
        "pensions": {
            "patterns": ["Pension", "RPP", "DCPP", "DBPP"],
            "requires_docs": ["pension statement", "commuted value statement"],
            "requires_value": True
        },
        "business_interests": {
            "patterns": ["Business", "Corporation", "Partnership", "Sole proprietorship"],
            "requires_docs": ["financial statements", "tax returns", "valuation report"],
            "requires_value": True
        }
    }
    
    DEBT_TABLES = {
        "mortgages": {
            "patterns": ["Mortgage", "Home equity", "HELOC"],
            "requires_docs": ["mortgage statement", "amortization schedule"],
            "requires_value": True
        },
        "loans": {
            "patterns": ["Loan", "Car loan", "Personal loan", "Student loan"],
            "requires_docs": ["loan statement", "payment schedule"],
            "requires_value": True
        },
        "credit_cards": {
            "patterns": ["Credit card", "Visa", "Mastercard", "Amex"],
            "requires_docs": ["statements (3 months)"],
            "requires_value": True,
            "statement_frequency": "monthly"
        },
        "taxes_owed": {
            "patterns": ["Tax", "CRA", "Income tax owing", "HST owing"],
            "requires_docs": ["notice of assessment", "statement of account"],
            "requires_value": True
        }
    }
    
    # Tax document requirements
    TAX_DOCUMENTS = {
        "t1_general": {
            "name": "T1 General Tax Return",
            "years": 3,
            "required": True,
            "includes": ["All schedules", "All slips"]
        },
        "notice_of_assessment": {
            "name": "Notice of Assessment",
            "years": 3,
            "required": True,
            "from": "CRA"
        },
        "t4": {
            "name": "T4 Statement of Remuneration",
            "years": 1,
            "required": True,
            "when": "if employed"
        },
        "t5": {
            "name": "T5 Investment Income",
            "years": 1,
            "required": False,
            "when": "if investments"
        },
        "t2125": {
            "name": "T2125 Business Income",
            "years": 3,
            "required": False,
            "when": "if self-employed"
        }
    }
    
    def __init__(self, form_path: str):
        self.form_path = Path(form_path)
        self.tables_detected = []
        self.document_requirements = []
        
    def parse(self) -> Dict:
        """
        Parse Form 13 to extract all financial tables and document requirements
        """
        logger.info(f"Enhanced parsing of Form 13: {self.form_path.name}")
        
        # Detect all table types
        self._detect_income_tables()
        self._detect_expense_tables()
        self._detect_asset_tables()
        self._detect_debt_tables()
        
        # Generate document requirements
        self._generate_document_requirements()
        
        # Create comprehensive report
        return self._generate_report()
    
    def _detect_income_tables(self):
        """Detect all income-related tables"""
        for income_type, config in self.INCOME_TABLES.items():
            table = FinancialTable(
                table_type="income",
                table_name=income_type.replace("_", " ").title(),
                table_id=f"income_{income_type}",
                page_number=0,  # Would be detected from actual parsing
                requires_statements=True,
                required_documents=config["requires_docs"]
            )
            
            # Add standard income columns
            table.columns = [
                {"name": "source", "label": "Source", "type": "text"},
                {"name": "monthly_amount", "label": "Monthly Amount", "type": "currency"},
                {"name": "annual_amount", "label": "Annual Amount", "type": "currency"},
                {"name": "documents", "label": "Supporting Documents", "type": "file_upload"}
            ]
            
            self.tables_detected.append(table)
    
    def _detect_expense_tables(self):
        """Detect all expense-related tables"""
        for expense_type, config in self.EXPENSE_TABLES.items():
            table = FinancialTable(
                table_type="expense",
                table_name=expense_type.replace("_", " ").title(),
                table_id=f"expense_{expense_type}",
                page_number=0,
                requires_statements=True,
                required_documents=config["requires_docs"]
            )
            
            # Add standard expense columns
            table.columns = [
                {"name": "description", "label": "Description", "type": "text"},
                {"name": "monthly_amount", "label": "Monthly Amount", "type": "currency"},
                {"name": "annual_amount", "label": "Annual Amount", "type": "currency"},
                {"name": "receipts", "label": "Receipts/Proof", "type": "file_upload"}
            ]
            
            self.tables_detected.append(table)
    
    def _detect_asset_tables(self):
        """Detect all asset-related tables with value requirements"""
        for asset_type, config in self.ASSET_TABLES.items():
            table = FinancialTable(
                table_type="asset",
                table_name=asset_type.replace("_", " ").title(),
                table_id=f"asset_{asset_type}",
                page_number=0,
                requires_value=config.get("requires_value", True),
                requires_statements=True,
                statement_frequency=config.get("statement_frequency", "annual"),
                required_documents=config["requires_docs"]
            )
            
            # Add asset-specific columns
            table.columns = [
                {"name": "description", "label": "Description", "type": "text"},
                {"name": "ownership", "label": "Ownership %", "type": "number"},
                {"name": "date_acquired", "label": "Date Acquired", "type": "date"},
                {"name": "original_value", "label": "Original Value", "type": "currency"},
                {"name": "current_value", "label": "Current Market Value", "type": "currency"},
                {"name": "statements", "label": "Statements/Valuations", "type": "file_upload_multiple"}
            ]
            
            # Special handling for bank accounts - need monthly statements
            if asset_type == "bank_accounts":
                table.columns.append({
                    "name": "monthly_statements",
                    "label": "Last 12 Monthly Statements",
                    "type": "file_upload_multiple",
                    "required": True,
                    "min_files": 12
                })
            
            self.tables_detected.append(table)
    
    def _detect_debt_tables(self):
        """Detect all debt-related tables"""
        for debt_type, config in self.DEBT_TABLES.items():
            table = FinancialTable(
                table_type="debt",
                table_name=debt_type.replace("_", " ").title(),
                table_id=f"debt_{debt_type}",
                page_number=0,
                requires_value=config.get("requires_value", True),
                requires_statements=True,
                statement_frequency=config.get("statement_frequency", "monthly"),
                required_documents=config["requires_docs"]
            )
            
            # Add debt-specific columns
            table.columns = [
                {"name": "creditor", "label": "Creditor Name", "type": "text"},
                {"name": "account_number", "label": "Account Number", "type": "text"},
                {"name": "date_incurred", "label": "Date Incurred", "type": "date"},
                {"name": "original_amount", "label": "Original Amount", "type": "currency"},
                {"name": "current_balance", "label": "Current Balance", "type": "currency"},
                {"name": "monthly_payment", "label": "Monthly Payment", "type": "currency"},
                {"name": "statements", "label": "Recent Statements", "type": "file_upload_multiple"}
            ]
            
            self.tables_detected.append(table)
    
    def _generate_document_requirements(self):
        """Generate comprehensive document upload requirements"""
        
        # Tax documents (always required)
        for tax_doc_id, config in self.TAX_DOCUMENTS.items():
            doc_req = DocumentRequirement(
                doc_type="tax_document",
                doc_name=config["name"],
                related_field="income",
                frequency="annual",
                years_required=config.get("years", 1),
                required=config.get("required", False),
                description=f"Please upload {config['name']} for the last {config.get('years', 1)} year(s)"
            )
            self.document_requirements.append(doc_req)
        
        # Pay stubs (if employed)
        self.document_requirements.append(DocumentRequirement(
            doc_type="pay_stub",
            doc_name="Recent Pay Stubs",
            related_field="employment_income",
            frequency="bi-weekly",
            years_required=0,
            required=True,
            description="Please upload your last 3 pay stubs"
        ))
        
        # Bank statements for ALL accounts
        self.document_requirements.append(DocumentRequirement(
            doc_type="bank_statement",
            doc_name="Bank Statements - All Accounts",
            related_field="bank_accounts",
            frequency="monthly",
            years_required=1,
            required=True,
            description="Upload 12 months of statements for EACH bank account"
        ))
        
        # Investment statements
        self.document_requirements.append(DocumentRequirement(
            doc_type="investment_statement",
            doc_name="Investment Account Statements",
            related_field="investments",
            frequency="quarterly",
            years_required=1,
            required=False,
            description="Upload quarterly statements for all investment accounts"
        ))
        
        # Property documents
        self.document_requirements.append(DocumentRequirement(
            doc_type="property_assessment",
            doc_name="Property Tax Assessment (MPAC)",
            related_field="real_estate",
            frequency="annual",
            years_required=1,
            required=False,
            description="Upload most recent property tax assessment for all properties"
        ))
        
        # Credit card statements
        self.document_requirements.append(DocumentRequirement(
            doc_type="credit_card_statement",
            doc_name="Credit Card Statements",
            related_field="credit_cards",
            frequency="monthly",
            years_required=0,
            required=True,
            description="Upload last 3 months of statements for all credit cards"
        ))
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive parsing report"""
        return {
            "form_type": "Form 13 - Financial Statement",
            "tables_detected": {
                "income_tables": [t for t in self.tables_detected if t.table_type == "income"],
                "expense_tables": [t for t in self.tables_detected if t.table_type == "expense"],
                "asset_tables": [t for t in self.tables_detected if t.table_type == "asset"],
                "debt_tables": [t for t in self.tables_detected if t.table_type == "debt"]
            },
            "document_requirements": {
                "tax_documents": [d for d in self.document_requirements if d.doc_type == "tax_document"],
                "income_verification": [d for d in self.document_requirements if "income" in d.related_field],
                "asset_verification": [d for d in self.document_requirements if "asset" in d.related_field or "bank" in d.related_field],
                "debt_verification": [d for d in self.document_requirements if "debt" in d.related_field or "credit" in d.related_field]
            },
            "summary": {
                "total_tables": len(self.tables_detected),
                "income_categories": len([t for t in self.tables_detected if t.table_type == "income"]),
                "expense_categories": len([t for t in self.tables_detected if t.table_type == "expense"]),
                "asset_categories": len([t for t in self.tables_detected if t.table_type == "asset"]),
                "debt_categories": len([t for t in self.tables_detected if t.table_type == "debt"]),
                "required_documents": len([d for d in self.document_requirements if d.required]),
                "optional_documents": len([d for d in self.document_requirements if not d.required])
            }
        }

def generate_docassemble_with_documents(tables: List[FinancialTable], 
                                       documents: List[DocumentRequirement]) -> str:
    """
    Generate docassemble YAML that includes document upload prompts
    """
    yaml_parts = []
    
    # Add metadata
    yaml_parts.append("""metadata:
  title: Form 13 - Financial Statement with Document Collection
  short_title: Financial Statement
  description: Complete financial disclosure with supporting documentation
---""")
    
    # Add objects for tables and documents
    yaml_parts.append("""objects:
  - user: Individual
  - income_items: DAList.using(object_type=IncomeItem)
  - expense_items: DAList.using(object_type=ExpenseItem)
  - assets: DAList.using(object_type=Asset)
  - debts: DAList.using(object_type=Debt)
  - tax_documents: DADict
  - bank_statements: DADict
  - support_documents: DADict
---""")
    
    # Add document upload screens
    yaml_parts.append("""question: Tax Returns and Notices of Assessment
subquestion: |
  Please upload your tax documents for the last 3 years.
  
  **Required Documents:**
  - T1 General Tax Return (complete with all schedules)
  - Notice of Assessment from CRA
  - All tax slips (T4, T5, etc.)
fields:
  - "Tax Year ${i}": tax_documents[i].year
    datatype: integer
    min: 2021
    max: 2024
  - "T1 Return for ${tax_documents[i].year}": tax_documents[i].t1_return
    datatype: file
    accept:
      - "application/pdf"
  - "Notice of Assessment for ${tax_documents[i].year}": tax_documents[i].noa
    datatype: file
    accept:
      - "application/pdf"
  - "Do you have more tax years to add?": tax_documents.there_is_another
    datatype: yesnoradio
---""")
    
    # Add asset-specific screens with document requirements
    for table in tables:
        if table.table_type == "asset" and table.requires_statements:
            yaml_parts.append(f"""question: {table.table_name} - Details and Documentation
subquestion: |
  For each {table.table_name.lower()}, provide:
  - Current market value
  - Supporting statements for the last {table.statement_frequency} period(s)
  
fields:
  - Description: assets[i].description
  - Current Value: assets[i].current_value
    datatype: currency
  - "Upload statements": assets[i].statements
    datatype: file
    accept:
      - "application/pdf"
      - "image/*"
    help: |
      % if "{table.table_id}" == "asset_bank_accounts":
      Upload the last 12 monthly statements for this account
      % elif "{table.table_id}" == "asset_investments":
      Upload quarterly statements for the last year
      % else:
      Upload the most recent statement or valuation
      % endif
---""")
    
    # Add validation for document completeness
    yaml_parts.append("""code: |
  documents_complete = True
  
  # Check tax documents (3 years required)
  if len(tax_documents) < 3:
    documents_complete = False
    validation_errors.append("Please upload tax documents for 3 years")
  
  # Check bank statements (12 months required for each account)
  for account in assets:
    if account.type == "bank_account":
      if not hasattr(account, 'statements') or len(account.statements) < 12:
        documents_complete = False
        validation_errors.append(f"Please upload 12 monthly statements for {account.description}")
---""")
    
    # Add review screen with document checklist
    yaml_parts.append("""review:
  - Document Checklist:
    button: |
      **Tax Documents:**
      % for year in tax_documents:
      - ${year}: T1 ✓ NOA ✓
      % endfor
      
      **Bank Statements:**
      % for account in assets:
      % if account.type == "bank_account":
      - ${account.description}: ${len(account.statements)} statements uploaded
      % endif
      % endfor
      
      **Other Supporting Documents:**
      - Pay stubs: ${len(pay_stubs)} uploaded
      - Investment statements: ${len(investment_statements)} uploaded
---""")
    
    return "\n".join(yaml_parts)

if __name__ == "__main__":
    # Test the enhanced parser
    parser = EnhancedForm13Parser("form_13.docx")
    result = parser.parse()
    
    print("=" * 80)
    print("ENHANCED FORM 13 PARSING RESULTS")
    print("=" * 80)
    
    print(f"\nTables Detected: {result['summary']['total_tables']}")
    print(f"  Income Tables: {result['summary']['income_categories']}")
    print(f"  Expense Tables: {result['summary']['expense_categories']}")
    print(f"  Asset Tables: {result['summary']['asset_categories']}")
    print(f"  Debt Tables: {result['summary']['debt_categories']}")
    
    print(f"\nDocument Requirements:")
    print(f"  Required Documents: {result['summary']['required_documents']}")
    print(f"  Optional Documents: {result['summary']['optional_documents']}")
    
    # Show sample asset table with document requirements
    asset_tables = result['tables_detected']['asset_tables']
    if asset_tables:
        print(f"\nSample Asset Table: {asset_tables[0].table_name}")
        print(f"  Requires Value: {asset_tables[0].requires_value}")
        print(f"  Requires Statements: {asset_tables[0].requires_statements}")
        print(f"  Statement Frequency: {asset_tables[0].statement_frequency}")
        print(f"  Required Documents: {', '.join(asset_tables[0].required_documents)}")
    
    # Save results
    output_path = Path("enhanced_form13_analysis.json")
    with open(output_path, 'w') as f:
        # Convert dataclasses to dicts for JSON serialization
        json_result = {
            "tables": [asdict(t) for t in parser.tables_detected],
            "documents": [asdict(d) for d in parser.document_requirements],
            "summary": result["summary"]
        }
        json.dump(json_result, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")