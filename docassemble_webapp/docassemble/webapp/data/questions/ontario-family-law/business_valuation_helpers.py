#!/usr/bin/env python3
"""
Business Valuation Helpers for Ontario Family Law
For integration with Docassemble Form 13 Financial Statement

This module provides helper functions for business valuation
and professional practice assessment in family law contexts.

Version: 1.0.0
Last Updated: 2025-08-09
"""

import decimal
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union


class BusinessValuationHelper:
    """
    Helper class for business valuation assessments in family law contexts.
    
    Provides guidance on valuation requirements, methods, and professional
    valuation thresholds for Ontario family law proceedings.
    """
    
    def __init__(self):
        """Initialize with current valuation parameters."""
        self.professional_valuation_threshold = decimal.Decimal('10000')
        self.significant_business_threshold = decimal.Decimal('50000')
        self.complex_business_threshold = decimal.Decimal('250000')
        
        # Common business types and their valuation considerations
        self.business_types = {
            'sole_proprietorship': {
                'complexity': 'Low to Medium',
                'valuation_methods': ['Asset-based', 'Income-based'],
                'typical_documents': ['Financial statements', 'Tax returns', 'Asset list'],
                'professional_required': False
            },
            'partnership': {
                'complexity': 'Medium to High',
                'valuation_methods': ['Income-based', 'Market-based', 'Asset-based'],
                'typical_documents': ['Partnership agreement', 'Financial statements', 'Buy-sell agreements'],
                'professional_required': True
            },
            'corporation': {
                'complexity': 'Medium to High',
                'valuation_methods': ['Market-based', 'Income-based', 'Asset-based'],
                'typical_documents': ['Corporate returns', 'Financial statements', 'Share agreements'],
                'professional_required': True
            },
            'professional_practice': {
                'complexity': 'High',
                'valuation_methods': ['Income-based', 'Market-based', 'Hybrid methods'],
                'typical_documents': ['Professional financial statements', 'Client lists', 'Equipment lists'],
                'professional_required': True
            }
        }
    
    def assess_valuation_requirements(self,
                                    business_type: str,
                                    estimated_value: Union[int, float, decimal.Decimal],
                                    annual_income: Union[int, float, decimal.Decimal],
                                    ownership_percentage: float = 100.0) -> Dict[str, Union[str, bool, List[str]]]:
        """
        Assess whether professional business valuation is required.
        
        Args:
            business_type: Type of business (sole_proprietorship, partnership, etc.)
            estimated_value: Estimated total business value
            annual_income: Annual income from business
            ownership_percentage: Percentage ownership (default 100%)
            
        Returns:
            Dictionary with assessment results and recommendations
        """
        try:
            value = decimal.Decimal(str(estimated_value))
            income = decimal.Decimal(str(annual_income))
            ownership = decimal.Decimal(str(ownership_percentage)) / 100
            
            # Calculate owner's share of value
            owner_value = value * ownership
            
            # Determine if professional valuation required
            professional_required = (
                owner_value >= self.professional_valuation_threshold or
                business_type in ['partnership', 'corporation', 'professional_practice'] or
                income >= 100000
            )
            
            # Assess complexity level
            if owner_value >= self.complex_business_threshold:
                complexity = 'High'
                priority = 'Urgent'
            elif owner_value >= self.significant_business_threshold:
                complexity = 'Medium-High'
                priority = 'High'
            elif owner_value >= self.professional_valuation_threshold:
                complexity = 'Medium'
                priority = 'Medium'
            else:
                complexity = 'Low'
                priority = 'Low'
            
            # Get business type information
            business_info = self.business_types.get(business_type, {
                'complexity': 'Unknown',
                'valuation_methods': ['Professional assessment required'],
                'typical_documents': ['All business records'],
                'professional_required': True
            })
            
            return {
                'professional_valuation_required': professional_required,
                'complexity_level': complexity,
                'priority': priority,
                'owner_value': owner_value,
                'recommended_methods': business_info['valuation_methods'],
                'required_documents': business_info['typical_documents'],
                'estimated_cost': self._estimate_valuation_cost(owner_value, business_type),
                'timeframe': self._estimate_valuation_timeframe(complexity, business_type),
                'recommendations': self._generate_recommendations(
                    professional_required, complexity, business_type, owner_value
                )
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Invalid input: {str(e)}',
                'professional_valuation_required': True,
                'recommendations': ['Consult with professional valuator due to input errors']
            }
    
    def _estimate_valuation_cost(self, value: decimal.Decimal, business_type: str) -> Dict[str, Union[str, decimal.Decimal]]:
        """Estimate professional valuation costs."""
        if value < self.professional_valuation_threshold:
            return {'range': '$500 - $2,000', 'notes': 'Basic assessment sufficient'}
        elif value < self.significant_business_threshold:
            return {'range': '$2,000 - $5,000', 'notes': 'Standard business valuation'}
        elif value < self.complex_business_threshold:
            return {'range': '$5,000 - $15,000', 'notes': 'Comprehensive valuation'}
        else:
            return {'range': '$15,000 - $50,000+', 'notes': 'Complex business requiring extensive analysis'}
    
    def _estimate_valuation_timeframe(self, complexity: str, business_type: str) -> str:
        """Estimate time required for professional valuation."""
        timeframes = {
            'Low': '2-4 weeks',
            'Medium': '4-8 weeks',
            'Medium-High': '6-12 weeks',
            'High': '8-16 weeks'
        }
        
        base_time = timeframes.get(complexity, '4-8 weeks')
        
        if business_type == 'professional_practice':
            return f"{base_time} (may be longer for professional practices)"
        
        return base_time
    
    def _generate_recommendations(self, professional_required: bool, complexity: str, 
                                business_type: str, value: decimal.Decimal) -> List[str]:
        """Generate specific recommendations based on business characteristics."""
        recommendations = []
        
        if professional_required:
            recommendations.append("Professional business valuation is required")
            recommendations.append("Engage a Chartered Business Valuator (CBV) or equivalent")
        
        if complexity == 'High':
            recommendations.append("Consider multiple valuation approaches")
            recommendations.append("Allow extra time for complex analysis")
        
        if business_type == 'professional_practice':
            recommendations.append("Ensure valuator has experience with professional practices")
            recommendations.append("Consider restrictions on practice transferability")
        
        if value >= self.complex_business_threshold:
            recommendations.append("Consider tax implications of valuation")
            recommendations.append("Review buy-sell agreements and partnership terms")
        
        recommendations.append("Gather 3-5 years of financial statements")
        recommendations.append("Prepare list of assets and liabilities")
        recommendations.append("Document key business relationships and contracts")
        
        return recommendations
    
    def recommend_valuators(self, business_type: str, location: str = 'Ontario') -> List[Dict[str, str]]:
        """
        Provide information about finding qualified business valuators.
        
        Args:
            business_type: Type of business requiring valuation
            location: Geographic location (default Ontario)
            
        Returns:
            List of recommendations for finding qualified valuators
        """
        general_resources = [
            {
                'organization': 'Canadian Institute of Chartered Business Valuators (CICBV)',
                'website': 'www.cicbv.ca',
                'description': 'Directory of Chartered Business Valuators',
                'specialization': 'All business types'
            },
            {
                'organization': 'American Society of Appraisers (ASA) - Canadian Chapter',
                'website': 'www.appraisers.org',
                'description': 'Business valuation specialists',
                'specialization': 'Complex business valuations'
            },
            {
                'organization': 'CPA Canada',
                'website': 'www.cpacanada.ca',
                'description': 'Accounting professionals with valuation expertise',
                'specialization': 'Financial analysis and valuation'
            }
        ]
        
        if business_type == 'professional_practice':
            general_resources.append({
                'organization': 'Professional Practice Brokers',
                'website': 'Various',
                'description': 'Specialists in professional practice valuations',
                'specialization': 'Medical, legal, dental, and other professional practices'
            })
        
        return general_resources
    
    def calculate_business_cash_flow(self,
                                   gross_revenue: Union[int, float, decimal.Decimal],
                                   operating_expenses: Union[int, float, decimal.Decimal],
                                   depreciation: Union[int, float, decimal.Decimal] = 0,
                                   owner_salary: Union[int, float, decimal.Decimal] = 0,
                                   discretionary_expenses: Union[int, float, decimal.Decimal] = 0) -> Dict[str, decimal.Decimal]:
        """
        Calculate normalized business cash flow for valuation purposes.
        
        Args:
            gross_revenue: Annual gross business revenue
            operating_expenses: Annual operating expenses
            depreciation: Annual depreciation expense
            owner_salary: Owner's salary/draws
            discretionary_expenses: Non-essential business expenses
            
        Returns:
            Dictionary with cash flow calculations
        """
        try:
            revenue = decimal.Decimal(str(gross_revenue))
            expenses = decimal.Decimal(str(operating_expenses))
            deprec = decimal.Decimal(str(depreciation))
            salary = decimal.Decimal(str(owner_salary))
            discretionary = decimal.Decimal(str(discretionary_expenses))
            
            # Basic cash flow calculation
            net_income = revenue - expenses
            
            # Add back non-cash expenses
            cash_flow_before_adjustments = net_income + deprec
            
            # Normalized cash flow (adding back discretionary items)
            normalized_cash_flow = cash_flow_before_adjustments + discretionary
            
            # Owner benefit (cash flow available to owner)
            owner_benefit = normalized_cash_flow + salary
            
            return {
                'gross_revenue': revenue,
                'net_income': net_income,
                'cash_flow_before_adjustments': cash_flow_before_adjustments,
                'normalized_cash_flow': normalized_cash_flow,
                'owner_benefit': owner_benefit,
                'revenue_multiple': normalized_cash_flow / revenue if revenue > 0 else decimal.Decimal('0'),
                'notes': 'Normalized cash flow removes discretionary and non-recurring items'
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'notes': 'Please verify all input amounts are valid numbers'
            }
    
    def estimate_business_value_range(self,
                                    annual_cash_flow: Union[int, float, decimal.Decimal],
                                    business_type: str,
                                    industry: str = 'general') -> Dict[str, Union[decimal.Decimal, str]]:
        """
        Provide rough business value estimates using common multiples.
        
        Note: This is for estimation only. Professional valuation required for legal purposes.
        
        Args:
            annual_cash_flow: Normalized annual cash flow
            business_type: Type of business
            industry: Industry sector
            
        Returns:
            Dictionary with estimated value ranges
        """
        try:
            cash_flow = decimal.Decimal(str(annual_cash_flow))
            
            if cash_flow <= 0:
                return {
                    'low_estimate': decimal.Decimal('0'),
                    'high_estimate': decimal.Decimal('0'),
                    'notes': 'Business with no cash flow has minimal going concern value'
                }
            
            # Common business valuation multiples (very rough estimates)
            multiples = {
                'sole_proprietorship': {'low': 1.5, 'high': 3.0},
                'partnership': {'low': 2.0, 'high': 4.0},
                'corporation': {'low': 2.5, 'high': 5.0},
                'professional_practice': {'low': 1.0, 'high': 2.5}
            }
            
            # Industry adjustments (simplified)
            industry_adjustments = {
                'technology': 1.2,
                'healthcare': 1.1,
                'manufacturing': 0.9,
                'retail': 0.8,
                'service': 1.0,
                'general': 1.0
            }
            
            base_multiples = multiples.get(business_type, {'low': 2.0, 'high': 4.0})
            industry_factor = decimal.Decimal(str(industry_adjustments.get(industry, 1.0)))
            
            low_multiple = decimal.Decimal(str(base_multiples['low'])) * industry_factor
            high_multiple = decimal.Decimal(str(base_multiples['high'])) * industry_factor
            
            low_estimate = cash_flow * low_multiple
            high_estimate = cash_flow * high_multiple
            
            return {
                'low_estimate': low_estimate.quantize(decimal.Decimal('1')),
                'high_estimate': high_estimate.quantize(decimal.Decimal('1')),
                'low_multiple': low_multiple,
                'high_multiple': high_multiple,
                'notes': 'ESTIMATE ONLY - Professional valuation required for legal proceedings',
                'warning': 'This is a rough estimate and should not be used for legal purposes'
            }
            
        except (ValueError, decimal.InvalidOperation) as e:
            return {
                'error': f'Calculation error: {str(e)}',
                'notes': 'Please verify cash flow amount is a valid number'
            }


# Convenience functions for Docassemble integration
def requires_professional_valuation(business_value: float, business_type: str) -> bool:
    """
    Simple function to determine if professional valuation is required.
    
    Args:
        business_value: Estimated business value
        business_type: Type of business
        
    Returns:
        True if professional valuation is required
    """
    helper = BusinessValuationHelper()
    assessment = helper.assess_valuation_requirements(business_type, business_value, 0)
    return assessment.get('professional_valuation_required', True)


def estimate_valuation_cost(business_value: float, business_type: str) -> str:
    """
    Estimate professional valuation cost for Docassemble templates.
    
    Args:
        business_value: Estimated business value
        business_type: Type of business
        
    Returns:
        Formatted cost estimate string
    """
    helper = BusinessValuationHelper()
    assessment = helper.assess_valuation_requirements(business_type, business_value, 0)
    cost_info = assessment.get('estimated_cost', {})
    return cost_info.get('range', 'Contact valuator for estimate')


def get_valuation_timeframe(business_value: float, business_type: str) -> str:
    """
    Get estimated timeframe for business valuation.
    
    Args:
        business_value: Estimated business value  
        business_type: Type of business
        
    Returns:
        Estimated timeframe string
    """
    helper = BusinessValuationHelper()
    assessment = helper.assess_valuation_requirements(business_type, business_value, 0)
    return assessment.get('timeframe', '4-8 weeks')


# Module-level instance
business_valuation_helper = BusinessValuationHelper()