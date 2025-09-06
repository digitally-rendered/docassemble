#!/usr/bin/env python3
"""
Ontario Financial Objects - Financial statement components for Ontario family law
Programmatically generates YAML objects for Form 13 Financial Statement and related financial information
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date
import calendar

@dataclass
class IncomeSource:
    """Individual income source"""
    source_type: str = ""  # employment, self_employment, investment, etc.
    description: str = ""
    gross_amount: float = 0.0
    net_amount: float = 0.0
    frequency: str = "annual"  # annual, monthly, weekly, etc.
    
    def annual_gross(self) -> float:
        """Convert to annual gross amount"""
        if self.frequency == "monthly":
            return self.gross_amount * 12
        elif self.frequency == "weekly":
            return self.gross_amount * 52
        elif self.frequency == "bi-weekly":
            return self.gross_amount * 26
        else:
            return self.gross_amount

@dataclass
class FinancialAsset:
    """Financial asset (bank account, investment, etc.)"""
    asset_type: str = ""  # bank_account, rrsp, investment, etc.
    description: str = ""
    institution: str = ""
    current_value: float = 0.0
    date_of_marriage_value: float = 0.0
    
    # Ownership details
    ownership: str = "sole"  # sole, joint, trust
    percentage_owned: float = 100.0

@dataclass
class RealEstate:
    """Real estate property"""
    property_type: str = ""  # matrimonial_home, other_residence, commercial, etc.
    address: str = ""
    current_value: float = 0.0
    date_of_marriage_value: float = 0.0
    mortgage_balance: float = 0.0
    
    # Ownership details
    ownership: str = "joint"  # sole, joint, tenants_in_common
    percentage_owned: float = 50.0
    
    # Property details
    purchase_date: Optional[date] = None
    is_matrimonial_home: bool = False

@dataclass
class Debt:
    """Debt or liability"""
    debt_type: str = ""  # credit_card, loan, mortgage, etc.
    creditor: str = ""
    current_balance: float = 0.0
    monthly_payment: float = 0.0
    
    # Debt details
    interest_rate: float = 0.0
    secured_by: str = ""  # what secures the debt
    responsibility: str = "sole"  # sole, joint, spouse_only

@dataclass
class MonthlyExpense:
    """Monthly living expense"""
    category: str = ""  # housing, food, transportation, etc.
    description: str = ""
    amount: float = 0.0
    
    # Expense details
    necessary: bool = True
    shared: bool = False  # shared with spouse/children

@dataclass
class OntarioFinancialStatement:
    """Complete Ontario Form 13 Financial Statement"""
    
    # Income information
    income_sources: List[IncomeSource] = field(default_factory=list)
    total_gross_income: float = 0.0
    total_net_income: float = 0.0
    
    # Assets
    financial_assets: List[FinancialAsset] = field(default_factory=list)
    real_estate: List[RealEstate] = field(default_factory=list)
    personal_property: List[FinancialAsset] = field(default_factory=list)  # cars, jewelry, etc.
    
    # Debts
    debts: List[Debt] = field(default_factory=list)
    
    # Monthly expenses
    monthly_expenses: List[MonthlyExpense] = field(default_factory=list)
    total_monthly_expenses: float = 0.0
    
    # Support information
    child_support_paid: float = 0.0
    child_support_received: float = 0.0
    spousal_support_paid: float = 0.0
    spousal_support_received: float = 0.0
    
    # Statement metadata
    statement_date: Optional[date] = None
    
    def calculate_total_assets(self) -> float:
        """Calculate total value of all assets"""
        total = 0.0
        
        for asset in self.financial_assets:
            total += asset.current_value * (asset.percentage_owned / 100)
        
        for property in self.real_estate:
            total += property.current_value * (property.percentage_owned / 100)
            
        for item in self.personal_property:
            total += item.current_value * (item.percentage_owned / 100)
        
        return total
    
    def calculate_total_debts(self) -> float:
        """Calculate total debt amount"""
        return sum(debt.current_balance for debt in self.debts if debt.responsibility in ["sole", "joint"])
    
    def calculate_net_worth(self) -> float:
        """Calculate net worth (assets - debts)"""
        return self.calculate_total_assets() - self.calculate_total_debts()
    
    def to_docassemble_objects(self) -> Dict[str, Any]:
        """Generate Docassemble objects for financial statement"""
        return {
            "total_gross_income": self.total_gross_income,
            "total_net_income": self.total_net_income,
            "total_assets": self.calculate_total_assets(),
            "total_debts": self.calculate_total_debts(),
            "net_worth": self.calculate_net_worth(),
            "total_monthly_expenses": self.total_monthly_expenses
        }

class OntarioFinancialGenerator:
    """Generates financial statement YAML objects for Ontario family law forms"""
    
    def __init__(self):
        self.income_questions = self._initialize_income_questions()
        self.asset_questions = self._initialize_asset_questions()
        self.debt_questions = self._initialize_debt_questions()
        self.expense_questions = self._initialize_expense_questions()
        
        self.income_categories = self._initialize_income_categories()
        self.asset_categories = self._initialize_asset_categories()
        self.expense_categories = self._initialize_expense_categories()
    
    def _initialize_income_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize income source categories"""
        return {
            "employment": {
                "title": "Employment Income",
                "description": "Salary, wages, tips, bonuses, commissions",
                "typical_deductions": ["income_tax", "cpp", "ei", "union_dues"]
            },
            "self_employment": {
                "title": "Self-Employment Income", 
                "description": "Income from business, farming, professional practice",
                "typical_deductions": ["business_expenses", "income_tax", "cpp"]
            },
            "investment": {
                "title": "Investment Income",
                "description": "Interest, dividends, capital gains, rental income", 
                "typical_deductions": ["income_tax"]
            },
            "pension": {
                "title": "Pension Income",
                "description": "CPP, OAS, company pension, RRIF withdrawals",
                "typical_deductions": ["income_tax"]
            },
            "government": {
                "title": "Government Benefits",
                "description": "EI, social assistance, disability benefits",
                "typical_deductions": []
            },
            "other": {
                "title": "Other Income",
                "description": "Any other regular income",
                "typical_deductions": []
            }
        }
    
    def _initialize_asset_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize asset categories"""
        return {
            "bank_accounts": {
                "title": "Bank Accounts",
                "examples": ["Chequing accounts", "Savings accounts", "Term deposits", "GICs"]
            },
            "investments": {
                "title": "Investments", 
                "examples": ["Stocks", "Bonds", "Mutual funds", "Investment accounts"]
            },
            "retirement": {
                "title": "Retirement Savings",
                "examples": ["RRSPs", "Pension plans", "RRIFs", "TFSAs"]
            },
            "real_estate": {
                "title": "Real Estate",
                "examples": ["Matrimonial home", "Other residences", "Rental properties", "Commercial property"]
            },
            "vehicles": {
                "title": "Vehicles",
                "examples": ["Cars", "Trucks", "Motorcycles", "Boats", "RVs"]
            },
            "personal_property": {
                "title": "Personal Property",
                "examples": ["Jewelry", "Art", "Collections", "Household contents", "Tools/equipment"]
            },
            "business": {
                "title": "Business Interests", 
                "examples": ["Business ownership", "Partnership interests", "Professional practice"]
            }
        }
    
    def _initialize_expense_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize expense categories"""
        return {
            "housing": {
                "title": "Housing",
                "examples": ["Rent/mortgage", "Property taxes", "Utilities", "Home insurance", "Maintenance"]
            },
            "food": {
                "title": "Food and Household",
                "examples": ["Groceries", "Household supplies", "Personal care items"]
            },
            "transportation": {
                "title": "Transportation",
                "examples": ["Car payments", "Insurance", "Gas", "Maintenance", "Public transit", "Parking"]
            },
            "healthcare": {
                "title": "Health Care",
                "examples": ["Medical expenses", "Dental", "Prescriptions", "Health insurance premiums"]
            },
            "children": {
                "title": "Children's Expenses",
                "examples": ["Childcare", "School supplies", "Activities", "Clothing", "Medical"]
            },
            "insurance": {
                "title": "Insurance",
                "examples": ["Life insurance", "Disability insurance", "Other insurance premiums"]
            },
            "debt": {
                "title": "Debt Payments", 
                "examples": ["Credit card payments", "Loan payments", "Other debt payments"]
            },
            "other": {
                "title": "Other Expenses",
                "examples": ["Entertainment", "Gifts", "Donations", "Professional fees"]
            }
        }
    
    def _initialize_income_questions(self) -> Dict[str, Any]:
        """Initialize income-related questions"""
        return {
            "employment_income": {
                "question": "Employment Income",
                "subquestion": "Provide details of your employment income from all sources",
                "fields": [
                    {"Employer name": "employment.employer_name"},
                    {"Job title": "employment.job_title"},
                    {"Annual salary/wages (before deductions)": "employment.annual_gross", "datatype": "currency"},
                    {"Annual net income (after deductions)": "employment.annual_net", "datatype": "currency"},
                    {"Pay frequency": "employment.pay_frequency", 
                     "datatype": "radio",
                     "choices": [
                         {"weekly": "Weekly"},
                         {"bi_weekly": "Bi-weekly (every 2 weeks)"},
                         {"monthly": "Monthly"},
                         {"annual": "Annual salary"}
                     ]},
                    {"Hours per week": "employment.hours_per_week", "datatype": "number", "required": False}
                ],
                "validation code": """
if employment.annual_gross <= 0:
  validation_error("Please enter a valid gross income amount")
if employment.annual_net > employment.annual_gross:
  validation_error("Net income cannot be higher than gross income")
"""
            },
            
            "self_employment_income": {
                "question": "Self-Employment Income",
                "subquestion": "If you are self-employed, provide business income details",
                "show if": "has_self_employment",
                "fields": [
                    {"Business name": "self_employment.business_name"},
                    {"Type of business": "self_employment.business_type"},
                    {"Annual gross business income": "self_employment.gross_income", "datatype": "currency"},
                    {"Annual business expenses": "self_employment.expenses", "datatype": "currency"},
                    {"Annual net business income": "self_employment.net_income", "datatype": "currency"}
                ],
                "validation code": """
if self_employment.net_income != (self_employment.gross_income - self_employment.expenses):
  validation_error("Net income should equal gross income minus expenses")
"""
            },
            
            "other_income": {
                "question": "Other Income Sources",
                "subquestion": "List any other regular income you receive",
                "fields": [
                    {"Investment income (interest, dividends)": "other_income.investment", "datatype": "currency", "required": False},
                    {"Rental income": "other_income.rental", "datatype": "currency", "required": False},
                    {"Pension income": "other_income.pension", "datatype": "currency", "required": False},
                    {"Government benefits (EI, social assistance)": "other_income.government", "datatype": "currency", "required": False},
                    {"Support received from others": "other_income.support_received", "datatype": "currency", "required": False},
                    {"Other income (describe)": "other_income.other", "datatype": "currency", "required": False},
                    {"Description of other income": "other_income.other_description", "required": False}
                ]
            }
        }
    
    def _initialize_asset_questions(self) -> Dict[str, Any]:
        """Initialize asset-related questions"""
        return {
            "bank_accounts": {
                "question": "Bank Accounts and Cash",
                "subquestion": "List all bank accounts, savings accounts, and cash holdings",
                "fields": [
                    {"Chequing accounts": "assets.chequing", "datatype": "currency", "required": False},
                    {"Savings accounts": "assets.savings", "datatype": "currency", "required": False},
                    {"Term deposits/GICs": "assets.term_deposits", "datatype": "currency", "required": False},
                    {"Cash on hand": "assets.cash", "datatype": "currency", "required": False}
                ]
            },
            
            "investments": {
                "question": "Investments",
                "subquestion": "List all investment accounts and holdings",
                "fields": [
                    {"RRSP accounts": "assets.rrsp", "datatype": "currency", "required": False},
                    {"TFSA accounts": "assets.tfsa", "datatype": "currency", "required": False},
                    {"Investment accounts (non-registered)": "assets.investments", "datatype": "currency", "required": False},
                    {"Pension plan value": "assets.pension", "datatype": "currency", "required": False},
                    {"Life insurance cash value": "assets.life_insurance", "datatype": "currency", "required": False}
                ]
            },
            
            "real_estate": {
                "question": "Real Estate",
                "subquestion": "List all real estate you own or have an interest in",
                "fields": [
                    {"Matrimonial home - current value": "real_estate.home_value", "datatype": "currency", "required": False},
                    {"Matrimonial home - mortgage balance": "real_estate.home_mortgage", "datatype": "currency", "required": False},
                    {"Other real estate - current value": "real_estate.other_value", "datatype": "currency", "required": False},
                    {"Other real estate - mortgage balance": "real_estate.other_mortgage", "datatype": "currency", "required": False}
                ]
            },
            
            "personal_property": {
                "question": "Personal Property",
                "subquestion": "List vehicles, jewelry, and other valuable personal property",
                "fields": [
                    {"Vehicles (cars, boats, etc.)": "assets.vehicles", "datatype": "currency", "required": False},
                    {"Jewelry and precious items": "assets.jewelry", "datatype": "currency", "required": False},
                    {"Household contents": "assets.household", "datatype": "currency", "required": False},
                    {"Collections, art, antiques": "assets.collections", "datatype": "currency", "required": False},
                    {"Business interests": "assets.business", "datatype": "currency", "required": False},
                    {"Other valuable property": "assets.other", "datatype": "currency", "required": False}
                ]
            }
        }
    
    def _initialize_debt_questions(self) -> Dict[str, Any]:
        """Initialize debt-related questions"""
        return {
            "secured_debts": {
                "question": "Secured Debts",
                "subquestion": "Debts secured by property (mortgages, car loans, etc.)",
                "fields": [
                    {"Mortgage on matrimonial home": "debts.home_mortgage", "datatype": "currency", "required": False},
                    {"Other mortgages": "debts.other_mortgages", "datatype": "currency", "required": False},
                    {"Car loans": "debts.car_loans", "datatype": "currency", "required": False},
                    {"Other secured loans": "debts.other_secured", "datatype": "currency", "required": False}
                ]
            },
            
            "unsecured_debts": {
                "question": "Unsecured Debts",
                "subquestion": "Credit cards, personal loans, and other unsecured debts",
                "fields": [
                    {"Credit cards": "debts.credit_cards", "datatype": "currency", "required": False},
                    {"Personal loans": "debts.personal_loans", "datatype": "currency", "required": False},
                    {"Student loans": "debts.student_loans", "datatype": "currency", "required": False},
                    {"Lines of credit": "debts.lines_of_credit", "datatype": "currency", "required": False},
                    {"Money owed to family/friends": "debts.family_loans", "datatype": "currency", "required": False},
                    {"Other debts": "debts.other", "datatype": "currency", "required": False}
                ]
            }
        }
    
    def _initialize_expense_questions(self) -> Dict[str, Any]:
        """Initialize expense-related questions"""
        return {
            "housing_expenses": {
                "question": "Housing Expenses",
                "subquestion": "Monthly costs for housing and utilities",
                "fields": [
                    {"Rent or mortgage payment": "expenses.housing_payment", "datatype": "currency"},
                    {"Property taxes (monthly)": "expenses.property_taxes", "datatype": "currency", "required": False},
                    {"Home insurance (monthly)": "expenses.home_insurance", "datatype": "currency", "required": False},
                    {"Utilities (heat, electricity, water)": "expenses.utilities", "datatype": "currency"},
                    {"Phone/internet/cable": "expenses.communications", "datatype": "currency"},
                    {"Home maintenance and repairs": "expenses.maintenance", "datatype": "currency", "required": False}
                ]
            },
            
            "living_expenses": {
                "question": "Living Expenses",
                "subquestion": "Monthly costs for food, transportation, and personal needs",
                "fields": [
                    {"Groceries and household supplies": "expenses.groceries", "datatype": "currency"},
                    {"Transportation (car payments, gas, insurance, transit)": "expenses.transportation", "datatype": "currency"},
                    {"Health care (medical, dental, prescriptions)": "expenses.healthcare", "datatype": "currency", "required": False},
                    {"Personal care (clothing, hair, etc.)": "expenses.personal_care", "datatype": "currency", "required": False},
                    {"Entertainment and recreation": "expenses.entertainment", "datatype": "currency", "required": False}
                ]
            },
            
            "children_expenses": {
                "question": "Children's Expenses",
                "subquestion": "Monthly costs related to children",
                "show if": "children.there_are_any",
                "fields": [
                    {"Childcare/daycare": "expenses.childcare", "datatype": "currency", "required": False},
                    {"Children's activities and sports": "expenses.activities", "datatype": "currency", "required": False},
                    {"Children's clothing": "expenses.children_clothing", "datatype": "currency", "required": False},
                    {"School supplies and fees": "expenses.school", "datatype": "currency", "required": False},
                    {"Children's medical/dental": "expenses.children_medical", "datatype": "currency", "required": False}
                ]
            },
            
            "other_expenses": {
                "question": "Other Monthly Expenses",
                "subquestion": "Any other regular monthly expenses",
                "fields": [
                    {"Life/disability insurance premiums": "expenses.insurance", "datatype": "currency", "required": False},
                    {"Debt payments (credit cards, loans)": "expenses.debt_payments", "datatype": "currency", "required": False},
                    {"Support paid to others": "expenses.support_paid", "datatype": "currency", "required": False},
                    {"Professional fees (legal, accounting)": "expenses.professional", "datatype": "currency", "required": False},
                    {"Donations and gifts": "expenses.donations", "datatype": "currency", "required": False},
                    {"Other expenses": "expenses.other", "datatype": "currency", "required": False}
                ]
            }
        }
    
    def generate_financial_objects(self) -> List[Dict[str, str]]:
        """Generate financial statement objects"""
        return [
            {"Thing": "financial_statement"},
            {"Thing": "income"},
            {"Thing": "employment"},
            {"Thing": "self_employment"},
            {"Thing": "other_income"},
            {"Thing": "assets"},
            {"Thing": "real_estate"},
            {"Thing": "debts"},
            {"Thing": "expenses"}
        ]
    
    def generate_income_questions(self) -> List[Dict[str, Any]]:
        """Generate income-related questions"""
        questions = []
        
        # Income source determination
        questions.append({
            "question": "What are your sources of income?",
            "subquestion": "Select all that apply to your situation",
            "fields": [
                {"Employment income": "has_employment", "datatype": "yesno"},
                {"Self-employment income": "has_self_employment", "datatype": "yesno"},
                {"Investment income": "has_investment", "datatype": "yesno"},
                {"Rental income": "has_rental", "datatype": "yesno"},
                {"Pension income": "has_pension", "datatype": "yesno"},
                {"Government benefits": "has_government", "datatype": "yesno"},
                {"Other income": "has_other_income", "datatype": "yesno"}
            ]
        })
        
        # Add specific income questions
        questions.append(self.income_questions["employment_income"])
        questions.append(self.income_questions["self_employment_income"])
        questions.append(self.income_questions["other_income"])
        
        # Income summary
        questions.append({
            "question": "Income Summary",
            "subquestion": """
% if has_employment:
**Employment Income:** ${currency(employment.annual_gross)}
% endif
% if has_self_employment:
**Self-Employment Income:** ${currency(self_employment.net_income)}
% endif
% if other_income.investment:
**Investment Income:** ${currency(other_income.investment)}
% endif
% if other_income.rental:
**Rental Income:** ${currency(other_income.rental)}
% endif
% if other_income.pension:
**Pension Income:** ${currency(other_income.pension)}
% endif
% if other_income.government:
**Government Benefits:** ${currency(other_income.government)}
% endif

**Total Annual Income:** ${currency(total_annual_income)}
""",
            "continue button field": "income_summary_reviewed",
            "code": "total_annual_income = calculate_total_income()"
        })
        
        return questions
    
    def generate_asset_questions(self) -> List[Dict[str, Any]]:
        """Generate asset-related questions"""
        questions = []
        
        questions.extend([
            self.asset_questions["bank_accounts"],
            self.asset_questions["investments"], 
            self.asset_questions["real_estate"],
            self.asset_questions["personal_property"]
        ])
        
        # Asset summary
        questions.append({
            "question": "Asset Summary",
            "subquestion": """
**Bank Accounts and Cash:** ${currency(total_liquid_assets)}
**Investments and Retirement:** ${currency(total_investments)}
**Real Estate:** ${currency(total_real_estate)}
**Personal Property:** ${currency(total_personal_property)}

**Total Assets:** ${currency(total_assets)}
""",
            "continue button field": "assets_summary_reviewed",
            "code": """
total_liquid_assets = (assets.chequing or 0) + (assets.savings or 0) + (assets.term_deposits or 0) + (assets.cash or 0)
total_investments = (assets.rrsp or 0) + (assets.tfsa or 0) + (assets.investments or 0) + (assets.pension or 0) + (assets.life_insurance or 0)
total_real_estate = ((real_estate.home_value or 0) - (real_estate.home_mortgage or 0)) + ((real_estate.other_value or 0) - (real_estate.other_mortgage or 0))
total_personal_property = (assets.vehicles or 0) + (assets.jewelry or 0) + (assets.household or 0) + (assets.collections or 0) + (assets.business or 0) + (assets.other or 0)
total_assets = total_liquid_assets + total_investments + total_real_estate + total_personal_property
"""
        })
        
        return questions
    
    def generate_debt_questions(self) -> List[Dict[str, Any]]:
        """Generate debt-related questions"""
        questions = []
        
        questions.extend([
            self.debt_questions["secured_debts"],
            self.debt_questions["unsecured_debts"]
        ])
        
        # Debt summary
        questions.append({
            "question": "Debt Summary", 
            "subquestion": """
**Secured Debts:** ${currency(total_secured_debts)}
**Unsecured Debts:** ${currency(total_unsecured_debts)}

**Total Debts:** ${currency(total_debts)}

**Net Worth (Assets - Debts):** ${currency(net_worth)}
""",
            "continue button field": "debts_summary_reviewed",
            "code": """
total_secured_debts = (debts.home_mortgage or 0) + (debts.other_mortgages or 0) + (debts.car_loans or 0) + (debts.other_secured or 0)
total_unsecured_debts = (debts.credit_cards or 0) + (debts.personal_loans or 0) + (debts.student_loans or 0) + (debts.lines_of_credit or 0) + (debts.family_loans or 0) + (debts.other or 0)
total_debts = total_secured_debts + total_unsecured_debts
net_worth = total_assets - total_debts
"""
        })
        
        return questions
    
    def generate_expense_questions(self) -> List[Dict[str, Any]]:
        """Generate expense-related questions"""
        questions = []
        
        questions.extend([
            self.expense_questions["housing_expenses"],
            self.expense_questions["living_expenses"],
            self.expense_questions["children_expenses"],
            self.expense_questions["other_expenses"]
        ])
        
        # Expense summary
        questions.append({
            "question": "Monthly Expense Summary",
            "subquestion": """
**Housing:** ${currency(total_housing_expenses)}
**Living Expenses:** ${currency(total_living_expenses)}
% if children.there_are_any:
**Children's Expenses:** ${currency(total_children_expenses)}
% endif
**Other Expenses:** ${currency(total_other_expenses)}

**Total Monthly Expenses:** ${currency(total_monthly_expenses)}
**Total Annual Expenses:** ${currency(total_monthly_expenses * 12)}

**Monthly Cash Flow:** ${currency(monthly_income - total_monthly_expenses)}
""",
            "continue button field": "expenses_summary_reviewed",
            "code": """
total_housing_expenses = (expenses.housing_payment or 0) + (expenses.property_taxes or 0) + (expenses.home_insurance or 0) + (expenses.utilities or 0) + (expenses.communications or 0) + (expenses.maintenance or 0)
total_living_expenses = (expenses.groceries or 0) + (expenses.transportation or 0) + (expenses.healthcare or 0) + (expenses.personal_care or 0) + (expenses.entertainment or 0)
total_children_expenses = (expenses.childcare or 0) + (expenses.activities or 0) + (expenses.children_clothing or 0) + (expenses.school or 0) + (expenses.children_medical or 0) if children.there_are_any else 0
total_other_expenses = (expenses.insurance or 0) + (expenses.debt_payments or 0) + (expenses.support_paid or 0) + (expenses.professional or 0) + (expenses.donations or 0) + (expenses.other or 0)
total_monthly_expenses = total_housing_expenses + total_living_expenses + total_children_expenses + total_other_expenses
monthly_income = total_annual_income / 12
"""
        })
        
        return questions
    
    def generate_financial_validation_code(self) -> str:
        """Generate financial validation functions"""
        return """
def calculate_total_income():
    '''Calculate total annual income from all sources'''
    total = 0
    
    if has_employment and employment.annual_gross:
        total += employment.annual_gross
    
    if has_self_employment and self_employment.net_income:
        total += self_employment.net_income
    
    if other_income.investment:
        total += other_income.investment
    
    if other_income.rental:
        total += other_income.rental
        
    if other_income.pension:
        total += other_income.pension
        
    if other_income.government:
        total += other_income.government
        
    if other_income.other:
        total += other_income.other
    
    return total

def validate_financial_amounts():
    '''Validate financial statement amounts are reasonable'''
    errors = []
    
    # Check for negative amounts where they shouldn't be
    if hasattr(employment, 'annual_gross') and employment.annual_gross < 0:
        errors.append("Employment income cannot be negative")
    
    # Check that net income is less than gross income
    if (hasattr(employment, 'annual_gross') and hasattr(employment, 'annual_net') and 
        employment.annual_net > employment.annual_gross):
        errors.append("Net employment income cannot be higher than gross income")
    
    # Check for unreasonably high amounts
    total_income = calculate_total_income()
    if total_income > 10000000:  # $10 million
        errors.append("Please verify the income amounts - they appear unusually high")
    
    # Check that expenses are reasonable compared to income
    monthly_income = total_income / 12
    if total_monthly_expenses > monthly_income * 2:
        errors.append("Monthly expenses appear high compared to income - please review")
    
    return errors

def estimate_support_capacity():
    '''Estimate capacity to pay support based on income and expenses'''
    monthly_income = calculate_total_income() / 12
    available_for_support = monthly_income - total_monthly_expenses
    
    return {
        'monthly_income': monthly_income,
        'monthly_expenses': total_monthly_expenses,
        'available_for_support': available_for_support,
        'support_capacity_percentage': (available_for_support / monthly_income * 100) if monthly_income > 0 else 0
    }
"""
    
    def generate_complete_financial_interview(self, form_number: str = "13") -> Dict[str, Any]:
        """Generate complete financial statement interview"""
        
        interview = {
            "metadata": {
                "title": f"Ontario Form {form_number} - Financial Statement",
                "short title": f"Form {form_number} Financial"
            },
            "objects": self.generate_financial_objects(),
            "mandatory": True,
            "code": "financial_statement_complete"
        }
        
        # Generate all question sections
        questions = []
        
        # Income section
        questions.extend(self.generate_income_questions())
        
        # Asset section  
        questions.extend(self.generate_asset_questions())
        
        # Debt section
        questions.extend(self.generate_debt_questions())
        
        # Expense section
        questions.extend(self.generate_expense_questions())
        
        # Final review
        questions.append({
            "question": "Financial Statement Complete",
            "subquestion": """
You have completed your financial statement. Here is a summary:

**Annual Income:** ${currency(total_annual_income)}
**Total Assets:** ${currency(total_assets)}
**Total Debts:** ${currency(total_debts)}
**Net Worth:** ${currency(net_worth)}
**Monthly Expenses:** ${currency(total_monthly_expenses)}
**Monthly Cash Flow:** ${currency(monthly_income - total_monthly_expenses)}

Please review all information carefully. You may be required to provide supporting documents such as:
- Recent tax returns or Notice of Assessment
- Pay stubs or employment letters
- Bank statements
- Investment statements
- Property assessments
- Debt statements

""",
            "continue button field": "financial_statement_complete"
        })
        
        interview["questions"] = questions
        
        return interview
    
    def generate_simplified_financial_questions(self) -> List[Dict[str, Any]]:
        """Generate simplified financial questions for forms that don't require full Form 13"""
        return [
            {
                "question": "What is your current annual income?",
                "subquestion": "Include income from all sources before taxes and deductions",
                "fields": [
                    {"Annual gross income": "simple_income.annual_gross", "datatype": "currency"}
                ],
                "validation code": """
if simple_income.annual_gross <= 0:
  validation_error("Please enter a valid income amount")
"""
            },
            {
                "question": "What are your main sources of income?",
                "fields": [
                    {"Employment": "simple_income.employment", "datatype": "currency", "required": False},
                    {"Self-employment": "simple_income.self_employment", "datatype": "currency", "required": False},
                    {"Investment": "simple_income.investment", "datatype": "currency", "required": False},
                    {"Pension/benefits": "simple_income.pension", "datatype": "currency", "required": False},
                    {"Other": "simple_income.other", "datatype": "currency", "required": False}
                ]
            }
        ]

# Global instance for easy import  
ontario_financial_generator = OntarioFinancialGenerator()