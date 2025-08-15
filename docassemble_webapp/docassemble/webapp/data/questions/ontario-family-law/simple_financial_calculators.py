#!/usr/bin/env python3
"""
Simple Financial Calculators for Ontario Family Law Form 13.1
Basic financial calculations for simplified financial statements

Version: 1.0.0
Last Updated: 2025-08-09
"""

import decimal
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Union


class SimpleFinancialCalculator:
    """
    Simple financial calculator for Form 13.1 Financial Statement.
    
    Provides basic calculations for income, expenses, assets, and liabilities
    without the complexity needed for Form 13.
    """
    
    def __init__(self):
        """Initialize with basic calculation parameters."""
        self.current_year = date.today().year
        self.months_per_year = 12
        
        # Basic expense categories for validation
        self.essential_expense_categories = [
            'housing', 'utilities', 'groceries', 'childcare', 
            'transportation', 'medical', 'insurance'
        ]
        
        # Income reasonableness thresholds
        self.minimum_wage_annual = decimal.Decimal('30000')  # Approximate Ontario minimum wage
        self.maximum_simple_income = decimal.Decimal('150000')  # Form 13.1 threshold
    
    def calculate_monthly_surplus_deficit(self,
                                       monthly_income: Union[int, float, decimal.Decimal],
                                       monthly_expenses: Union[int, float, decimal.Decimal]) -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Calculate monthly surplus or deficit.
        
        Args:
            monthly_income: Total monthly income
            monthly_expenses: Total monthly expenses
            
        Returns:
            Dictionary with surplus/deficit calculation and assessment
        """
        try:
            income = decimal.Decimal(str(monthly_income))
            expenses = decimal.Decimal(str(monthly_expenses))
            
            surplus_deficit = income - expenses
            
            # Assess the situation
            if surplus_deficit > 0:
                status = 'Surplus'
                assessment = 'Income exceeds expenses'
                if surplus_deficit > income * decimal.Decimal('0.3'):
                    concern_level = 'Low'
                    notes = 'Healthy financial situation'
                else:
                    concern_level = 'Medium'
                    notes = 'Moderate surplus available'
            elif surplus_deficit == 0:
                status = 'Break-even'
                assessment = 'Income equals expenses'
                concern_level = 'Medium'
                notes = 'No surplus available for additional obligations'
            else:  # Deficit
                status = 'Deficit'
                assessment = 'Expenses exceed income'
                deficit_percentage = abs(surplus_deficit) / income * 100 if income > 0 else 100
                
                if deficit_percentage > 20:
                    concern_level = 'High'
                    notes = 'Significant deficit - financial adjustment needed'
                elif deficit_percentage > 10:
                    concern_level = 'Medium'
                    notes = 'Moderate deficit - budget review recommended'
                else:
                    concern_level = 'Low'
                    notes = 'Minor deficit - manageable with adjustments'
            
            return {
                'surplus_deficit': surplus_deficit.quantize(decimal.Decimal('0.01')),
                'status': status,
                'assessment': assessment,
                'concern_level': concern_level,
                'notes': notes,
                'annual_surplus_deficit': (surplus_deficit * 12).quantize(decimal.Decimal('0.01'))
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'notes': 'Please verify income and expense amounts'
            }
    
    def calculate_net_worth(self,
                          total_assets: Union[int, float, decimal.Decimal],
                          total_debts: Union[int, float, decimal.Decimal]) -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Calculate simple net worth.
        
        Args:
            total_assets: Total value of assets
            total_debts: Total debt obligations
            
        Returns:
            Dictionary with net worth calculation and assessment
        """
        try:
            assets = decimal.Decimal(str(total_assets))
            debts = decimal.Decimal(str(total_debts))
            
            net_worth = assets - debts
            
            # Assess financial position
            if net_worth > 0:
                if net_worth > assets * decimal.Decimal('0.5'):
                    position = 'Strong'
                    notes = 'Good asset-to-debt ratio'
                else:
                    position = 'Moderate'
                    notes = 'Reasonable financial position'
            elif net_worth == 0:
                position = 'Break-even'
                notes = 'Assets equal debts'
            else:  # Negative net worth
                position = 'Deficit'
                notes = 'Debts exceed assets - debt reduction recommended'
            
            # Calculate debt-to-asset ratio
            debt_ratio = (debts / assets * 100) if assets > 0 else decimal.Decimal('100')
            
            return {
                'net_worth': net_worth.quantize(decimal.Decimal('0.01')),
                'financial_position': position,
                'debt_to_asset_ratio': debt_ratio.quantize(decimal.Decimal('0.1')),
                'notes': notes,
                'total_assets': assets,
                'total_debts': debts
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'notes': 'Please verify asset and debt amounts'
            }
    
    def validate_income_for_form_131(self,
                                   annual_income: Union[int, float, decimal.Decimal]) -> Dict[str, Union[bool, str]]:
        """
        Validate income for Form 13.1 eligibility.
        
        Args:
            annual_income: Annual gross income
            
        Returns:
            Dictionary with validation results
        """
        try:
            income = decimal.Decimal(str(annual_income))
            
            if income < 0:
                return {
                    'valid': False,
                    'eligible_for_131': False,
                    'message': 'Income cannot be negative',
                    'recommendation': 'Enter zero if no income, or actual income amount'
                }
            
            if income == 0:
                return {
                    'valid': True,
                    'eligible_for_131': True,
                    'message': 'Zero income reported',
                    'recommendation': 'Consider if income should be imputed. Court may assess earning capacity.'
                }
            
            if income >= self.maximum_simple_income:
                return {
                    'valid': True,
                    'eligible_for_131': False,
                    'message': f'Income of ${income:,.2f} exceeds $150,000 threshold',
                    'recommendation': 'Form 13 (Complex) is required for income over $150,000'
                }
            
            if income < self.minimum_wage_annual:
                return {
                    'valid': True,
                    'eligible_for_131': True,
                    'message': 'Income below minimum wage level',
                    'recommendation': 'Verify this represents actual income. Court may impute higher income.'
                }
            
            return {
                'valid': True,
                'eligible_for_131': True,
                'message': 'Income within Form 13.1 range',
                'recommendation': 'Form 13.1 is appropriate for this income level'
            }
            
        except (ValueError, decimal.InvalidOperation):
            return {
                'valid': False,
                'eligible_for_131': False,
                'message': 'Invalid income format',
                'recommendation': 'Enter income as a number (e.g., 45000 for $45,000)'
            }
    
    def calculate_basic_child_support_estimate(self,
                                             annual_income: Union[int, float, decimal.Decimal],
                                             num_children: int,
                                             province: str = 'Ontario') -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Provide basic child support estimate for Form 13.1 purposes.
        
        Note: This is a simplified estimate. Official tables must be used for actual calculations.
        
        Args:
            annual_income: Annual gross income
            num_children: Number of children
            province: Province (default Ontario)
            
        Returns:
            Dictionary with basic support estimate
        """
        try:
            income = decimal.Decimal(str(annual_income))
            
            if income <= 0:
                return {
                    'monthly_estimate': decimal.Decimal('0'),
                    'annual_estimate': decimal.Decimal('0'),
                    'notes': 'No support payable with zero income',
                    'disclaimer': 'Court may impute income based on earning capacity'
                }
            
            # Very simplified calculation (approximation only)
            # Real calculation requires official Child Support Guidelines tables
            
            base_percentage_per_child = {
                1: decimal.Decimal('0.20'),  # ~20% for 1 child
                2: decimal.Decimal('0.32'),  # ~32% for 2 children  
                3: decimal.Decimal('0.42'),  # ~42% for 3 children
                4: decimal.Decimal('0.50')   # ~50% for 4+ children
            }
            
            # Use appropriate percentage
            children_count = min(num_children, 4)
            percentage = base_percentage_per_child.get(children_count, decimal.Decimal('0.20'))
            
            # Apply to first $150,000 of income (simplified)
            income_for_calculation = min(income, decimal.Decimal('150000'))
            
            # Basic calculation
            annual_estimate = income_for_calculation * percentage / 12  # Monthly amount
            
            # Very rough approximation - not legally accurate
            if income < 30000:
                annual_estimate = annual_estimate * decimal.Decimal('0.5')  # Lower income adjustment
            elif income > 100000:
                annual_estimate = annual_estimate * decimal.Decimal('1.1')  # Higher income adjustment
            
            monthly_estimate = annual_estimate
            annual_total = monthly_estimate * 12
            
            return {
                'monthly_estimate': monthly_estimate.quantize(decimal.Decimal('0.01')),
                'annual_estimate': annual_total.quantize(decimal.Decimal('0.01')),
                'notes': f'Rough estimate for {num_children} child{"ren" if num_children > 1 else ""}',
                'disclaimer': 'ESTIMATE ONLY - Use official Child Support Guidelines tables for accurate amounts',
                'warning': 'This is not an official calculation and should not be relied upon for legal purposes'
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'notes': 'Please verify income and number of children'
            }
    
    def assess_expense_reasonableness(self,
                                    monthly_expenses: Dict[str, Union[int, float, decimal.Decimal]],
                                    monthly_income: Union[int, float, decimal.Decimal],
                                    household_size: int = 1) -> Dict[str, Union[str, List[str]]]:
        """
        Assess whether reported expenses are reasonable.
        
        Args:
            monthly_expenses: Dictionary of expense categories and amounts
            monthly_income: Monthly income
            household_size: Number of people in household
            
        Returns:
            Dictionary with reasonableness assessment
        """
        try:
            income = decimal.Decimal(str(monthly_income))
            total_expenses = decimal.Decimal('0')
            assessments = []
            warnings = []
            
            # Calculate total expenses
            for category, amount in monthly_expenses.items():
                expense_amount = decimal.Decimal(str(amount)) if amount else decimal.Decimal('0')
                total_expenses += expense_amount
                
                # Check for unusually high expenses
                if category == 'housing' and expense_amount > income * decimal.Decimal('0.5'):
                    warnings.append(f'Housing costs ({expense_amount}) exceed 50% of income')
                elif category == 'groceries' and expense_amount > 200 * household_size:
                    warnings.append(f'Grocery costs seem high for household size of {household_size}')
                elif category == 'entertainment' and expense_amount > income * decimal.Decimal('0.15'):
                    warnings.append('Entertainment expenses exceed 15% of income')
            
            # Overall assessment
            expense_ratio = total_expenses / income if income > 0 else decimal.Decimal('0')
            
            if expense_ratio > decimal.Decimal('1.2'):
                overall_assessment = 'Expenses significantly exceed income - review required'
                concern_level = 'High'
            elif expense_ratio > decimal.Decimal('1.0'):
                overall_assessment = 'Expenses exceed income - budget adjustment needed'
                concern_level = 'Medium'
            elif expense_ratio > decimal.Decimal('0.9'):
                overall_assessment = 'Expenses are reasonable but leave little surplus'
                concern_level = 'Low'
            else:
                overall_assessment = 'Expenses appear reasonable relative to income'
                concern_level = 'None'
            
            return {
                'overall_assessment': overall_assessment,
                'concern_level': concern_level,
                'expense_to_income_ratio': (expense_ratio * 100).quantize(decimal.Decimal('0.1')),
                'warnings': warnings,
                'total_monthly_expenses': total_expenses.quantize(decimal.Decimal('0.01')),
                'recommendations': self._generate_expense_recommendations(warnings, concern_level)
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Assessment error: {str(e)}',
                'notes': 'Please verify all expense amounts are valid numbers'
            }
    
    def _generate_expense_recommendations(self, warnings: List[str], concern_level: str) -> List[str]:
        """Generate recommendations based on expense assessment."""
        recommendations = []
        
        if concern_level == 'High':
            recommendations.extend([
                'Review and reduce non-essential expenses',
                'Consider increasing income if possible',
                'Prioritize essential expenses (housing, food, childcare)'
            ])
        elif concern_level == 'Medium':
            recommendations.extend([
                'Look for areas to reduce expenses',
                'Create a detailed budget plan',
                'Monitor spending closely'
            ])
        
        if any('Housing costs' in warning for warning in warnings):
            recommendations.append('Consider housing alternatives if possible')
        
        if any('Grocery costs' in warning for warning in warnings):
            recommendations.append('Review grocery spending and meal planning')
        
        if any('Entertainment' in warning for warning in warnings):
            recommendations.append('Reduce discretionary entertainment expenses')
        
        if not recommendations:
            recommendations.append('Expenses appear reasonable - continue current spending patterns')
        
        return recommendations
    
    def calculate_debt_service_ratio(self,
                                   monthly_debt_payments: Union[int, float, decimal.Decimal],
                                   monthly_gross_income: Union[int, float, decimal.Decimal]) -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Calculate debt service ratio.
        
        Args:
            monthly_debt_payments: Total monthly debt payments
            monthly_gross_income: Monthly gross income
            
        Returns:
            Dictionary with debt service ratio analysis
        """
        try:
            debt_payments = decimal.Decimal(str(monthly_debt_payments))
            income = decimal.Decimal(str(monthly_gross_income))
            
            if income <= 0:
                return {
                    'debt_service_ratio': decimal.Decimal('0'),
                    'assessment': 'Cannot calculate with zero income',
                    'recommendation': 'Review income and debt obligations'
                }
            
            ratio = debt_payments / income * 100
            
            # Assess debt service ratio
            if ratio <= 20:
                assessment = 'Good'
                recommendation = 'Debt load is manageable'
                concern_level = 'Low'
            elif ratio <= 30:
                assessment = 'Acceptable'
                recommendation = 'Debt load is reasonable but monitor carefully'
                concern_level = 'Medium'
            elif ratio <= 40:
                assessment = 'High'
                recommendation = 'Consider debt reduction strategies'
                concern_level = 'High'
            else:
                assessment = 'Very High'
                recommendation = 'Immediate debt reduction required - consider professional help'
                concern_level = 'Critical'
            
            return {
                'debt_service_ratio': ratio.quantize(decimal.Decimal('0.1')),
                'assessment': assessment,
                'concern_level': concern_level,
                'recommendation': recommendation,
                'monthly_debt_payments': debt_payments,
                'monthly_income': income
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'recommendation': 'Please verify debt payment and income amounts'
            }


# Convenience functions for Docassemble integration
def calculate_monthly_surplus(monthly_income: float, monthly_expenses: float) -> str:
    """
    Simple surplus/deficit calculation for templates.
    
    Args:
        monthly_income: Monthly income amount
        monthly_expenses: Monthly expense amount
        
    Returns:
        Formatted surplus/deficit amount
    """
    calculator = SimpleFinancialCalculator()
    result = calculator.calculate_monthly_surplus_deficit(monthly_income, monthly_expenses)
    
    if 'error' in result:
        return 'Calculation error'
    
    amount = result['surplus_deficit']
    if amount >= 0:
        return f"${amount:.2f} surplus"
    else:
        return f"${abs(amount):.2f} deficit"


def is_eligible_for_form_131(annual_income: float) -> bool:
    """
    Check Form 13.1 eligibility based on income.
    
    Args:
        annual_income: Annual gross income
        
    Returns:
        True if eligible for Form 13.1
    """
    calculator = SimpleFinancialCalculator()
    result = calculator.validate_income_for_form_131(annual_income)
    return result.get('eligible_for_131', False)


def estimate_simple_child_support(annual_income: float, num_children: int) -> str:
    """
    Simple child support estimate for Form 13.1.
    
    Args:
        annual_income: Annual gross income
        num_children: Number of children
        
    Returns:
        Formatted monthly support estimate
    """
    calculator = SimpleFinancialCalculator()
    result = calculator.calculate_basic_child_support_estimate(annual_income, num_children)
    
    if 'error' in result:
        return 'See Child Support Guidelines'
    
    return f"${result['monthly_estimate']:.2f}/month (estimate)"


# Module-level instance
simple_financial_calculator = SimpleFinancialCalculator()