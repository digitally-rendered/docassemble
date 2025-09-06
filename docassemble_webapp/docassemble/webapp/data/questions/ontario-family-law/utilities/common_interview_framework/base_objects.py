"""
Base Objects for Ontario Family Law Forms
Provides common object definitions used across all forms.
"""
from docassemble.base.core import DAObject, DAList
from docassemble.base.util import Individual, Address, Person, Value
from docassemble.base.functions import currency

class OntarioCourtCase(DAObject):
    """Represents an Ontario court case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.court_file_number = ""
        self.court_name = ""
        self.court_address = Address()
        self.case_type = ""
        self.filing_date = None
    
    def court_file_formatted(self):
        """Return formatted court file number"""
        if self.court_file_number:
            # Format: XX-YY-NNNNNNNN
            return self.court_file_number.upper().replace(' ', '').replace('-', '')[:2] + '-' + \
                   self.court_file_number.upper().replace(' ', '').replace('-', '')[2:4] + '-' + \
                   self.court_file_number.upper().replace(' ', '').replace('-', '')[4:]
        return ""

class OntarioParty(Person):
    """Represents a party (applicant/respondent) in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.party_type = ""  # applicant, respondent, etc.
        self.represented_by_lawyer = None
        self.lawyer = Individual()
        self.phone_number = ""
        self.email = ""
        self.date_of_birth = None
        self.occupation = ""
        self.employer = ""
    
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class OntarioChild(Individual):
    """Represents a child in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.date_of_birth = None
        self.lives_with = ""  # applicant, respondent, other
        self.school = ""
        self.special_needs = ""
        self.custody_arrangement = ""
        self.access_arrangement = ""
    
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def is_minor(self):
        """Check if child is under 18"""
        age = self.age()
        return age is not None and age < 18

class OntarioChildList(DAList):
    """List of children in Ontario family law case"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.object_type = OntarioChild
    
    def minor_children(self):
        """Return list of children under 18"""
        return [child for child in self if child.is_minor()]
    
    def adult_children(self):
        """Return list of children 18 or older"""
        return [child for child in self if not child.is_minor()]

class FinancialInformation(DAObject):
    """Represents financial information for a party"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.annual_income = Value()
        self.monthly_income = Value()
        self.employment_income = Value()
        self.other_income = Value()
        self.expenses = Value()
        self.assets = Value()
        self.debts = Value()
    
    def net_worth(self):
        """Calculate net worth (assets - debts)"""
        return currency(self.assets.amount - self.debts.amount)
    
    def monthly_disposable_income(self):
        """Calculate monthly disposable income"""
        return currency(self.monthly_income.amount - self.expenses.amount)

class SupportAmount(DAObject):
    """Represents support payment information"""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.amount = Value()
        self.frequency = ""  # monthly, weekly, etc.
        self.start_date = None
        self.end_date = None
        self.support_type = ""  # child, spousal, etc.
    
    def monthly_amount(self):
        """Convert to monthly amount regardless of frequency"""
        if self.frequency == "weekly":
            return currency(self.amount.amount * 52 / 12)
        elif self.frequency == "bi-weekly":
            return currency(self.amount.amount * 26 / 12)
        elif self.frequency == "monthly":
            return currency(self.amount.amount)
        elif self.frequency == "annual":
            return currency(self.amount.amount / 12)
        return self.amount
