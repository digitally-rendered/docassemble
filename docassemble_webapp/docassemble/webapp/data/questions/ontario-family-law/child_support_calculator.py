#!/usr/bin/env python3
"""
Ontario Child Support Guidelines Calculator
For integration with Docassemble Ontario Family Law Forms

This module provides functions to calculate child support amounts
according to the Federal Child Support Guidelines as applied in Ontario.

Version: 1.0.0
Last Updated: 2025-08-09
"""

import decimal
from datetime import date
from typing import Dict, List, Optional, Tuple, Union


class ChildSupportCalculator:
    """
    Calculator for Federal Child Support Guidelines amounts in Ontario.
    
    This class provides methods to calculate table amounts, special expenses,
    and total child support obligations according to the Federal Child Support
    Guidelines as implemented in Ontario.
    """
    
    def __init__(self):
        """Initialize the calculator with current guideline parameters."""
        self.current_year = date.today().year
        self.table_threshold = decimal.Decimal('150000')  # Income level where table amounts cap
        
        # Base monthly amounts for Ontario (2024 guidelines - approximate)
        # These are simplified amounts for demonstration
        # Real implementation would use official tables
        self.base_table_amounts = {
            1: {  # One child
                30000: 256,
                40000: 341,
                50000: 426,
                60000: 511,
                70000: 596,
                80000: 681,
                90000: 766,
                100000: 851,
                120000: 1021,
                150000: 1276
            },
            2: {  # Two children
                30000: 405,
                40000: 540,
                50000: 675,
                60000: 809,
                70000: 944,
                80000: 1079,
                90000: 1214,
                100000: 1349,
                120000: 1618,
                150000: 2023
            },
            3: {  # Three children
                30000: 548,
                40000: 730,
                50000: 912,
                60000: 1094,
                70000: 1276,
                80000: 1458,
                90000: 1640,
                100000: 1822,
                120000: 2186,
                150000: 2733
            },
            4: {  # Four children
                30000: 659,
                40000: 878,
                50000: 1097,
                60000: 1316,
                70000: 1535,
                80000: 1754,
                90000: 1973,
                100000: 2192,
                120000: 2630,
                150000: 3288
            }
        }
    
    def calculate_table_amount(self, 
                             annual_income: Union[int, float, decimal.Decimal],
                             num_children: int,
                             province: str = 'Ontario') -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Calculate the basic table amount for child support.
        
        Args:
            annual_income: Annual gross income
            num_children: Number of children requiring support
            province: Province (default Ontario)
            
        Returns:
            Dictionary containing calculation results
        """
        try:
            income = decimal.Decimal(str(annual_income))
            
            if income < 0:
                return {
                    'monthly_amount': decimal.Decimal('0'),
                    'annual_amount': decimal.Decimal('0'),
                    'calculation_method': 'No income - no support payable',
                    'notes': 'Support may still be imputed based on earning capacity'
                }
            
            if income < 10000:
                return {
                    'monthly_amount': decimal.Decimal('0'),
                    'annual_amount': decimal.Decimal('0'),
                    'calculation_method': 'Income below guideline threshold',
                    'notes': 'Court may impute income or order nominal support'
                }
            
            # Cap children at 6 for table purposes
            children_for_calculation = min(num_children, 6)
            
            if children_for_calculation > 4:
                # For more than 4 children, use 4-child amount plus additional calculation
                base_amount = self._get_table_amount_for_income(income, 4)
                additional_children = children_for_calculation - 4
                additional_amount = base_amount * decimal.Decimal('0.3') * additional_children
                monthly_amount = base_amount + additional_amount
                calculation_method = f'Table amount for 4 children plus {additional_children * 30}% for additional children'
            else:
                monthly_amount = self._get_table_amount_for_income(income, children_for_calculation)
                calculation_method = f'Table amount for {children_for_calculation} child{"ren" if children_for_calculation > 1 else ""}'
            
            # Handle income over table threshold
            if income > self.table_threshold:
                notes = f'Income over ${self.table_threshold:,}. Court has discretion for additional amount.'
            else:
                notes = 'Standard table amount applies'
            
            return {
                'monthly_amount': monthly_amount.quantize(decimal.Decimal('0.01')),
                'annual_amount': (monthly_amount * 12).quantize(decimal.Decimal('0.01')),
                'calculation_method': calculation_method,
                'notes': notes,
                'income_used': income,
                'children_count': num_children
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'monthly_amount': decimal.Decimal('0'),
                'annual_amount': decimal.Decimal('0'),
                'calculation_method': 'Error in calculation',
                'notes': f'Calculation error: {str(e)}'
            }
    
    def _get_table_amount_for_income(self, income: decimal.Decimal, num_children: int) -> decimal.Decimal:
        """
        Get table amount for specific income and number of children.
        Uses interpolation between table values.
        """
        if num_children not in self.base_table_amounts:
            # For more children than in table, estimate
            base_amount = self._get_table_amount_for_income(income, min(num_children, 4))
            if num_children > 4:
                return base_amount * decimal.Decimal('1.2')  # Rough estimate
            return base_amount
        
        table = self.base_table_amounts[num_children]
        income_levels = sorted(table.keys())
        
        # If income is at or below lowest level
        if income <= income_levels[0]:
            return decimal.Decimal(str(table[income_levels[0]]))
        
        # If income is at or above highest level
        if income >= income_levels[-1]:
            return decimal.Decimal(str(table[income_levels[-1]]))
        
        # Find the two income levels to interpolate between
        for i, level in enumerate(income_levels):
            if income <= level:
                lower_income = income_levels[i-1]
                upper_income = level
                lower_amount = decimal.Decimal(str(table[lower_income]))
                upper_amount = decimal.Decimal(str(table[upper_income]))
                
                # Linear interpolation
                income_range = upper_income - lower_income
                amount_range = upper_amount - lower_amount
                position = (income - lower_income) / income_range
                
                return lower_amount + (amount_range * position)
        
        # Fallback (shouldn't reach here)
        return decimal.Decimal(str(table[income_levels[-1]]))
    
    def calculate_special_expenses(self,
                                 expenses: Dict[str, Union[int, float, decimal.Decimal]],
                                 payor_income: Union[int, float, decimal.Decimal],
                                 recipient_income: Union[int, float, decimal.Decimal] = 0) -> Dict[str, decimal.Decimal]:
        """
        Calculate special or extraordinary expenses sharing.
        
        Args:
            expenses: Dictionary of expense categories and amounts
            payor_income: Income of support payor
            recipient_income: Income of support recipient
            
        Returns:
            Dictionary with expense sharing calculations
        """
        try:
            payor_inc = decimal.Decimal(str(payor_income))
            recipient_inc = decimal.Decimal(str(recipient_income))
            total_income = payor_inc + recipient_inc
            
            if total_income == 0:
                return {'error': 'Combined income cannot be zero'}
            
            # Calculate proportional sharing
            payor_percentage = payor_inc / total_income
            recipient_percentage = recipient_inc / total_income
            
            total_expenses = decimal.Decimal('0')
            expense_breakdown = {}
            
            for category, amount in expenses.items():
                expense_amount = decimal.Decimal(str(amount))
                total_expenses += expense_amount
                
                payor_share = expense_amount * payor_percentage
                recipient_share = expense_amount * recipient_percentage
                
                expense_breakdown[category] = {
                    'total_amount': expense_amount,
                    'payor_share': payor_share.quantize(decimal.Decimal('0.01')),
                    'recipient_share': recipient_share.quantize(decimal.Decimal('0.01'))
                }
            
            return {
                'total_special_expenses': total_expenses,
                'payor_percentage': (payor_percentage * 100).quantize(decimal.Decimal('0.1')),
                'recipient_percentage': (recipient_percentage * 100).quantize(decimal.Decimal('0.1')),
                'payor_total_share': sum(exp['payor_share'] for exp in expense_breakdown.values()),
                'recipient_total_share': sum(exp['recipient_share'] for exp in expense_breakdown.values()),
                'expense_breakdown': expense_breakdown
            }
            
        except (ValueError, decimal.InvalidOperation, ZeroDivisionError) as e:
            return {'error': f'Calculation error: {str(e)}'}
    
    def calculate_total_support(self,
                              annual_income: Union[int, float, decimal.Decimal],
                              num_children: int,
                              special_expenses: Optional[Dict[str, Union[int, float, decimal.Decimal]]] = None,
                              recipient_income: Union[int, float, decimal.Decimal] = 0) -> Dict[str, decimal.Decimal]:
        """
        Calculate total child support including table amount and special expenses.
        
        Args:
            annual_income: Annual gross income of payor
            num_children: Number of children
            special_expenses: Dictionary of special expenses
            recipient_income: Income of support recipient
            
        Returns:
            Dictionary with complete support calculation
        """
        # Calculate table amount
        table_result = self.calculate_table_amount(annual_income, num_children)
        
        result = {
            'table_amount_monthly': table_result['monthly_amount'],
            'table_amount_annual': table_result['annual_amount'],
            'calculation_notes': [table_result['notes']]
        }
        
        # Calculate special expenses if provided
        if special_expenses:
            special_result = self.calculate_special_expenses(
                special_expenses, annual_income, recipient_income
            )
            
            if 'error' not in special_result:
                result.update({
                    'special_expenses_monthly': (special_result['payor_total_share'] / 12).quantize(decimal.Decimal('0.01')),
                    'special_expenses_annual': special_result['payor_total_share'],
                    'special_expense_breakdown': special_result['expense_breakdown']
                })
                
                result['total_monthly'] = result['table_amount_monthly'] + result['special_expenses_monthly']
                result['total_annual'] = result['table_amount_annual'] + result['special_expenses_annual']
            else:
                result['special_expense_error'] = special_result['error']
                result['total_monthly'] = result['table_amount_monthly']
                result['total_annual'] = result['table_amount_annual']
        else:
            result['total_monthly'] = result['table_amount_monthly']
            result['total_annual'] = result['table_amount_annual']
        
        return result
    
    def validate_income_for_guidelines(self, income: Union[int, float, decimal.Decimal]) -> Dict[str, Union[bool, str]]:
        """
        Validate income for child support guidelines purposes.
        
        Args:
            income: Annual income to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            inc = decimal.Decimal(str(income))
            
            if inc < 0:
                return {
                    'valid': False,
                    'message': 'Income cannot be negative',
                    'recommendation': 'Enter actual income or zero if no income'
                }
            
            if inc == 0:
                return {
                    'valid': True,
                    'message': 'Zero income - court may impute income',
                    'recommendation': 'Consider whether income should be imputed based on earning capacity'
                }
            
            if inc < 10000:
                return {
                    'valid': True,
                    'message': 'Low income - may qualify for special provisions',
                    'recommendation': 'Review low-income provisions in guidelines'
                }
            
            if inc > 1000000:
                return {
                    'valid': True,
                    'message': 'Very high income - court discretion applies',
                    'recommendation': 'Additional support beyond table amounts may be ordered'
                }
            
            return {
                'valid': True,
                'message': 'Income within normal guidelines range',
                'recommendation': 'Standard table amounts apply'
            }
            
        except (ValueError, decimal.InvalidOperation):
            return {
                'valid': False,
                'message': 'Invalid income format',
                'recommendation': 'Enter numeric income amount'
            }


# Convenience functions for Docassemble integration
def calculate_ontario_child_support(income: float, children: int) -> str:
    """
    Simple function for basic child support calculation in Docassemble templates.
    
    Args:
        income: Annual gross income
        children: Number of children
        
    Returns:
        Formatted monthly support amount
    """
    calculator = ChildSupportCalculator()
    result = calculator.calculate_table_amount(income, children)
    return f"${result['monthly_amount']:.2f}/month"


def calculate_child_support_with_expenses(income: float, 
                                        children: int, 
                                        childcare: float = 0,
                                        medical: float = 0,
                                        educational: float = 0) -> Dict[str, str]:
    """
    Calculate child support with common special expenses.
    
    Args:
        income: Annual gross income
        children: Number of children
        childcare: Annual childcare costs
        medical: Annual medical/dental costs
        educational: Annual educational costs
        
    Returns:
        Dictionary with formatted amounts
    """
    calculator = ChildSupportCalculator()
    
    special_expenses = {}
    if childcare > 0:
        special_expenses['childcare'] = childcare
    if medical > 0:
        special_expenses['medical'] = medical
    if educational > 0:
        special_expenses['educational'] = educational
    
    result = calculator.calculate_total_support(
        income, children, special_expenses if special_expenses else None
    )
    
    return {
        'table_amount': f"${result['table_amount_monthly']:.2f}/month",
        'special_expenses': f"${result.get('special_expenses_monthly', 0):.2f}/month" if special_expenses else "$0.00/month",
        'total_amount': f"${result['total_monthly']:.2f}/month",
        'annual_total': f"${result['total_annual']:.2f}/year"
    }


# Module-level instance for direct use
ontario_child_support = ChildSupportCalculator()