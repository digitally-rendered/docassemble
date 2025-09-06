/**
 * Playwright tests for Ontario Family Law Form 13
 * Generated from YAML interview: generated_interviews/form_13_interview.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Form 13: Form 13

 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
test.describe.configure({ mode: 'parallel' });

// Test data
const testData = {
  'court.file_number': 'Test Court file number',
  'court.location': 'Test Court location',
  'applicant.name.text': 'Test Full legal name',
  'applicant.address.address': 'Test Street address',
  'applicant.address.city': 'Test City',
  'applicant.address.province': 'Test Province',
  'applicant.address.postal_code': 'Test Postal code',
  'applicant.phone_number': '416-555-0123',
  'applicant.email': 'test@example.com',
  'respondent.name.text': 'Test Full legal name',
  'respondent.address.address': 'Test Street address',
  'respondent.address.city': 'Test City',
  'respondent.address.province': 'Test Province',
  'respondent.address.postal_code': 'Test Postal code',
  'respondent.phone_number': '416-555-0123',
  'respondent.email': 'test@example.com',
  '10_10_child_tax_benefits_or_ta': '1000.00',
  'cell_phone_cell_phone_cell_pho': '1000.00',
  'pet_care_pet_care_pet_care_pet': '1000.00',
  'childcare_costs_childcare_cost': '1000.00',
  'daycare_expense_daycare_expens': '1000.00',
  '_medical_insurance_premiums_an': '1000.00',
  '4_last_year_my_gross_income_fr': '1000.00',
  'financial.employment_income': '1000.00',
  '6_6_social_assistance_income_i': '1000.00',
  '7_7_interest_and_investment_in': '1000.00',
  '8_8_pension_income_including_c': '1000.00',
  '11_11_other_sources_of_income_': '1000.00',
  '12_12_total_monthly_income_fro': '1000.00',
  '13_13_total_monthly_income_x_1': '1000.00',
  'income_taxes_income_taxes_inco': '1000.00',
  'property_insurance_property_in': '1000.00',
  'subtotal_subtotal_subtotal_sub': '1000.00',
  'household_expenses_household_e': '1000.00',
  'babysitting_costs_babysitting_': '1000.00',
  'financial.monthly_expenses': '1000.00',
  'total_amount_of_yearly_expense': '1000.00',
  'other_assets_other_assets_1_': '1000.00',
  'other_assets_other_assets_2_': '1000.00',
  'other_assets_other_assets_3_': '1000.00',
  'other_debts_other_debts_other_': '1000.00',
  'total_amount_of_debts_outstand': '1000.00',
  'total_assets_total_assets_tota': '1000.00',
  'subtract_total_debts_subtract_': '1000.00',
  '1_1_net_partnership_income_net': '1000.00',
  '2_2_net_rental_income_gross_an': '1000.00',
  '6_6_income_from_a_registered_r': '1000.00',
  '7_7_any_other_income_specify_s': '1000.00',
  'i_earn_per_year_which_should_b': '1000.00',
  'property_taxes_property_taxes_': '1000.00',
  'total_value_of_all_property_to': '1000.00',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 13 - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Wait for the interview to load
    await page.waitForSelector('.da-page-header', { timeout: 10000 });
    
    // Fill fields for: Court Information

    await page.fill('[name="court.file_number"]', testData['court.file_number'] || 'Test Value');
    await page.fill('[name="court.location"]', testData['court.location'] || 'Test Value');
    await page.fill('[name="ontario_court_locations()
"]', testData['ontario_court_locations()
'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Applicant Information

    await page.fill('[name="applicant.name.text"]', testData['applicant.name.text'] || 'Test Value');
    await page.fill('[name="applicant.address.address"]', testData['applicant.address.address'] || 'Test Value');
    await page.fill('[name="applicant.address.city"]', testData['applicant.address.city'] || 'Test Value');
    await page.fill('[name="applicant.address.province"]', testData['applicant.address.province'] || 'Test Value');
    await page.fill('[name="applicant.address.postal_code"]', testData['applicant.address.postal_code'] || 'Test Value');
    await page.fill('[name="applicant.phone_number"]', testData['applicant.phone_number'] || 'Test Value');
    await page.fill('[name="applicant.email"]', testData['applicant.email'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Respondent Information

    await page.fill('[name="respondent.name.text"]', testData['respondent.name.text'] || 'Test Value');
    await page.fill('[name="respondent.address.address"]', testData['respondent.address.address'] || 'Test Value');
    await page.fill('[name="respondent.address.city"]', testData['respondent.address.city'] || 'Test Value');
    await page.fill('[name="respondent.address.province"]', testData['respondent.address.province'] || 'Test Value');
    await page.fill('[name="respondent.address.postal_code"]', testData['respondent.address.postal_code'] || 'Test Value');
    await page.fill('[name="respondent.phone_number"]', testData['respondent.phone_number'] || 'Test Value');
    await page.fill('[name="respondent.email"]', testData['respondent.email'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Children Information

    await page.fill('[name="10_10_child_tax_benefits_or_ta"]', testData['10_10_child_tax_benefits_or_ta'] || 'Test Value');
    await page.fill('[name="cell_phone_cell_phone_cell_pho"]', testData['cell_phone_cell_phone_cell_pho'] || 'Test Value');
    await page.fill('[name="pet_care_pet_care_pet_care_pet"]', testData['pet_care_pet_care_pet_care_pet'] || 'Test Value');
    await page.fill('[name="childcare_costs_childcare_cost"]', testData['childcare_costs_childcare_cost'] || 'Test Value');
    await page.fill('[name="daycare_expense_daycare_expens"]', testData['daycare_expense_daycare_expens'] || 'Test Value');
    await page.fill('[name="_medical_insurance_premiums_an"]', testData['_medical_insurance_premiums_an'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Financial Information

    await page.fill('[name="4_last_year_my_gross_income_fr"]', testData['4_last_year_my_gross_income_fr'] || 'Test Value');
    await page.fill('[name="financial.employment_income"]', testData['financial.employment_income'] || 'Test Value');
    await page.fill('[name="6_6_social_assistance_income_i"]', testData['6_6_social_assistance_income_i'] || 'Test Value');
    await page.fill('[name="7_7_interest_and_investment_in"]', testData['7_7_interest_and_investment_in'] || 'Test Value');
    await page.fill('[name="8_8_pension_income_including_c"]', testData['8_8_pension_income_including_c'] || 'Test Value');
    await page.fill('[name="11_11_other_sources_of_income_"]', testData['11_11_other_sources_of_income_'] || 'Test Value');
    await page.fill('[name="12_12_total_monthly_income_fro"]', testData['12_12_total_monthly_income_fro'] || 'Test Value');
    await page.fill('[name="13_13_total_monthly_income_x_1"]', testData['13_13_total_monthly_income_x_1'] || 'Test Value');
    await page.fill('[name="income_taxes_income_taxes_inco"]', testData['income_taxes_income_taxes_inco'] || 'Test Value');
    await page.fill('[name="property_insurance_property_in"]', testData['property_insurance_property_in'] || 'Test Value');
    await page.fill('[name="subtotal_subtotal_subtotal_sub"]', testData['subtotal_subtotal_subtotal_sub'] || 'Test Value');
    await page.fill('[name="household_expenses_household_e"]', testData['household_expenses_household_e'] || 'Test Value');
    await page.fill('[name="babysitting_costs_babysitting_"]', testData['babysitting_costs_babysitting_'] || 'Test Value');
    await page.fill('[name="financial.monthly_expenses"]', testData['financial.monthly_expenses'] || 'Test Value');
    await page.fill('[name="total_amount_of_yearly_expense"]', testData['total_amount_of_yearly_expense'] || 'Test Value');
    await page.fill('[name="other_assets_other_assets_1_"]', testData['other_assets_other_assets_1_'] || 'Test Value');
    await page.fill('[name="other_assets_other_assets_2_"]', testData['other_assets_other_assets_2_'] || 'Test Value');
    await page.fill('[name="other_assets_other_assets_3_"]', testData['other_assets_other_assets_3_'] || 'Test Value');
    await page.fill('[name="other_debts_other_debts_other_"]', testData['other_debts_other_debts_other_'] || 'Test Value');
    await page.fill('[name="total_amount_of_debts_outstand"]', testData['total_amount_of_debts_outstand'] || 'Test Value');
    await page.fill('[name="total_assets_total_assets_tota"]', testData['total_assets_total_assets_tota'] || 'Test Value');
    await page.fill('[name="subtract_total_debts_subtract_"]', testData['subtract_total_debts_subtract_'] || 'Test Value');
    await page.fill('[name="1_1_net_partnership_income_net"]', testData['1_1_net_partnership_income_net'] || 'Test Value');
    await page.fill('[name="2_2_net_rental_income_gross_an"]', testData['2_2_net_rental_income_gross_an'] || 'Test Value');
    await page.fill('[name="6_6_income_from_a_registered_r"]', testData['6_6_income_from_a_registered_r'] || 'Test Value');
    await page.fill('[name="7_7_any_other_income_specify_s"]', testData['7_7_any_other_income_specify_s'] || 'Test Value');
    await page.fill('[name="i_earn_per_year_which_should_b"]', testData['i_earn_per_year_which_should_b'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Property Information

    await page.fill('[name="property_taxes_property_taxes_"]', testData['property_taxes_property_taxes_'] || 'Test Value');
    await page.fill('[name="total_value_of_all_property_to"]', testData['total_value_of_all_property_to'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 13 - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

});

test.describe('Form 13 - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Move forward a few screens
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');
    
    // Test back button
    const backButton = page.locator('button:has-text("Back")');
    if (await backButton.isVisible()) {
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify we went back
      await expect(page).toHaveURL(/.*question.*/);
    }
  });
  
  test('Test progress bar updates', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    const progressBar = page.locator('.progress-bar, [role="progressbar"]');
    if (await progressBar.isVisible()) {
      const initialProgress = await progressBar.getAttribute('aria-valuenow') || 
                             await progressBar.getAttribute('style');
      
      // Move forward
      await page.click('button:has-text("Continue")');
      await page.waitForLoadState('networkidle');
      
      const newProgress = await progressBar.getAttribute('aria-valuenow') || 
                         await progressBar.getAttribute('style');
      
      // Progress should have increased
      expect(newProgress).not.toBe(initialProgress);
    }
  });
});

test.describe('Form 13 - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Fill some data
    const firstInput = page.locator('input[type="text"]').first();
    if (await firstInput.isVisible()) {
      await firstInput.fill('Test Data');
    }
    
    // Refresh page
    await page.reload();
    
    // Interview should resume
    await expect(page.locator('.da-page-header')).toBeVisible();
  });
  
  test('Verify mobile responsiveness', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    
    // Check that content is visible and accessible
    await expect(page.locator('.da-page-header')).toBeVisible();
    await expect(page.locator('button:has-text("Continue")')).toBeVisible();
    
    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  });
});

// Performance tests
test.describe('Form 13 - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 13 loaded in ${loadTime}ms`);
  });
});
