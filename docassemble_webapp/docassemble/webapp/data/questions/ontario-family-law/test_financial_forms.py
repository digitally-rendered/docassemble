#!/usr/bin/env python3
"""
Basic Test Suite for Ontario Family Law Financial Forms
Tests the calculation modules and basic functionality

Version: 1.0.0
Last Updated: 2025-08-09
"""

import sys
import os
import unittest
import decimal

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from child_support_calculator import ChildSupportCalculator, calculate_ontario_child_support
    from business_valuation_helpers import BusinessValuationHelper, requires_professional_valuation
    from simple_financial_calculators import SimpleFinancialCalculator, is_eligible_for_form_131
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all calculator modules are in the same directory")
    sys.exit(1)


class TestChildSupportCalculator(unittest.TestCase):
    """Test the child support calculator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ChildSupportCalculator()
    
    def test_basic_child_support_calculation(self):
        """Test basic child support table amount calculation."""
        # Test with income of $60,000 and 1 child
        result = self.calculator.calculate_table_amount(60000, 1)
        
        self.assertIn('monthly_amount', result)
        self.assertIn('annual_amount', result)
        self.assertGreater(result['monthly_amount'], 0)
        self.assertEqual(result['annual_amount'], result['monthly_amount'] * 12)
    
    def test_zero_income(self):
        """Test child support calculation with zero income."""
        result = self.calculator.calculate_table_amount(0, 1)
        
        self.assertEqual(result['monthly_amount'], decimal.Decimal('0'))
        self.assertIn('below guideline threshold', result['calculation_method'])
    
    def test_high_income(self):
        """Test child support calculation with high income."""
        result = self.calculator.calculate_table_amount(200000, 2)
        
        self.assertGreater(result['monthly_amount'], 0)
        self.assertIn('discretion', result['notes'])
    
    def test_multiple_children(self):
        """Test child support calculation with multiple children."""
        result_1_child = self.calculator.calculate_table_amount(75000, 1)
        result_2_children = self.calculator.calculate_table_amount(75000, 2)
        
        self.assertGreater(result_2_children['monthly_amount'], result_1_child['monthly_amount'])
    
    def test_special_expenses(self):
        """Test special expenses calculation."""
        expenses = {
            'childcare': 6000,
            'medical': 1200
        }
        
        result = self.calculator.calculate_special_expenses(expenses, 80000, 40000)
        
        self.assertIn('payor_total_share', result)
        self.assertIn('recipient_total_share', result)
        self.assertGreater(result['payor_total_share'], result['recipient_total_share'])
    
    def test_income_validation(self):
        """Test income validation for guidelines."""
        # Valid income
        result = self.calculator.validate_income_for_guidelines(50000)
        self.assertTrue(result['valid'])
        
        # Negative income
        result = self.calculator.validate_income_for_guidelines(-1000)
        self.assertFalse(result['valid'])
        
        # Very high income
        result = self.calculator.validate_income_for_guidelines(1500000)
        self.assertTrue(result['valid'])
        self.assertIn('discretion', result['message'])


class TestBusinessValuationHelper(unittest.TestCase):
    """Test the business valuation helper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.helper = BusinessValuationHelper()
    
    def test_valuation_requirements_small_business(self):
        """Test valuation requirements for small business."""
        result = self.helper.assess_valuation_requirements(
            'sole_proprietorship', 5000, 30000
        )
        
        self.assertFalse(result['professional_valuation_required'])
        self.assertEqual(result['complexity_level'], 'Low')
    
    def test_valuation_requirements_significant_business(self):
        """Test valuation requirements for significant business."""
        result = self.helper.assess_valuation_requirements(
            'corporation', 100000, 80000
        )
        
        self.assertTrue(result['professional_valuation_required'])
        self.assertIn('complexity_level', result)
        self.assertIn('estimated_cost', result)
    
    def test_professional_practice_valuation(self):
        """Test valuation requirements for professional practice."""
        result = self.helper.assess_valuation_requirements(
            'professional_practice', 200000, 150000
        )
        
        self.assertTrue(result['professional_valuation_required'])
        self.assertIn(result['complexity_level'], ['Medium-High', 'High'])
        self.assertIn('professional practice', result['timeframe'])
    
    def test_cash_flow_calculation(self):
        """Test business cash flow calculation."""
        result = self.helper.calculate_business_cash_flow(
            gross_revenue=200000,
            operating_expenses=120000,
            depreciation=10000,
            owner_salary=40000,
            discretionary_expenses=5000
        )
        
        self.assertIn('net_income', result)
        self.assertIn('normalized_cash_flow', result)
        self.assertIn('owner_benefit', result)
        self.assertEqual(result['net_income'], decimal.Decimal('80000'))
    
    def test_business_value_estimation(self):
        """Test business value estimation."""
        result = self.helper.estimate_business_value_range(
            annual_cash_flow=50000,
            business_type='corporation',
            industry='service'
        )
        
        self.assertIn('low_estimate', result)
        self.assertIn('high_estimate', result)
        self.assertGreater(result['high_estimate'], result['low_estimate'])
        self.assertIn('ESTIMATE ONLY', result['notes'])


class TestSimpleFinancialCalculator(unittest.TestCase):
    """Test the simple financial calculator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = SimpleFinancialCalculator()
    
    def test_surplus_deficit_calculation(self):
        """Test monthly surplus/deficit calculation."""
        # Surplus case
        result = self.calculator.calculate_monthly_surplus_deficit(5000, 4000)
        
        self.assertEqual(result['surplus_deficit'], decimal.Decimal('1000'))
        self.assertEqual(result['status'], 'Surplus')
        
        # Deficit case  
        result = self.calculator.calculate_monthly_surplus_deficit(3000, 4000)
        
        self.assertEqual(result['surplus_deficit'], decimal.Decimal('-1000'))
        self.assertEqual(result['status'], 'Deficit')
    
    def test_net_worth_calculation(self):
        """Test net worth calculation."""
        result = self.calculator.calculate_net_worth(150000, 100000)
        
        self.assertEqual(result['net_worth'], decimal.Decimal('50000'))
        self.assertIn(result['financial_position'], ['Strong', 'Moderate', 'Break-even', 'Deficit'])
    
    def test_form_131_eligibility(self):
        """Test Form 13.1 eligibility validation."""
        # Eligible income
        result = self.calculator.validate_income_for_form_131(75000)
        
        self.assertTrue(result['valid'])
        self.assertTrue(result['eligible_for_131'])
        
        # Income too high for Form 13.1
        result = self.calculator.validate_income_for_form_131(180000)
        
        self.assertTrue(result['valid'])
        self.assertFalse(result['eligible_for_131'])
        self.assertIn('Form 13', result['recommendation'])
    
    def test_child_support_estimate(self):
        """Test basic child support estimate."""
        result = self.calculator.calculate_basic_child_support_estimate(60000, 1)
        
        self.assertIn('monthly_estimate', result)
        self.assertGreater(result['monthly_estimate'], 0)
        self.assertIn('ESTIMATE ONLY', result['disclaimer'])
    
    def test_expense_reasonableness(self):
        """Test expense reasonableness assessment."""
        expenses = {
            'housing': 1500,
            'groceries': 600,
            'utilities': 200,
            'entertainment': 300
        }
        
        result = self.calculator.assess_expense_reasonableness(
            expenses, 4000, household_size=2
        )
        
        self.assertIn('overall_assessment', result)
        self.assertIn('expense_to_income_ratio', result)
        self.assertEqual(result['total_monthly_expenses'], decimal.Decimal('2600'))
    
    def test_debt_service_ratio(self):
        """Test debt service ratio calculation."""
        result = self.calculator.calculate_debt_service_ratio(1200, 5000)
        
        self.assertEqual(result['debt_service_ratio'], decimal.Decimal('24.0'))
        self.assertIn('assessment', result)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for Docassemble integration."""
    
    def test_ontario_child_support_function(self):
        """Test the convenience function for child support."""
        result = calculate_ontario_child_support(60000, 1)
        
        self.assertIn('$', result)
        self.assertIn('/month', result)
    
    def test_professional_valuation_required(self):
        """Test the professional valuation requirement function."""
        # Should require professional valuation
        self.assertTrue(requires_professional_valuation(50000, 'corporation'))
        
        # Should not require professional valuation
        self.assertFalse(requires_professional_valuation(5000, 'sole_proprietorship'))
    
    def test_form_131_eligibility_function(self):
        """Test the Form 13.1 eligibility function."""
        # Should be eligible
        self.assertTrue(is_eligible_for_form_131(75000))
        
        # Should not be eligible (too high income)
        self.assertFalse(is_eligible_for_form_131(180000))


def run_tests():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("Ontario Family Law Financial Forms - Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestChildSupportCalculator,
        TestBusinessValuationHelper, 
        TestSimpleFinancialCalculator,
        TestConvenienceFunctions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, failure in result.failures:
            print(f"- {test}: {failure.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error.split(':')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed! Financial forms calculations are working correctly.")
        return True
    else:
        print("\n✗ Some tests failed. Please review and fix issues before deployment.")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)