/**
 * Playwright tests for Ontario Family Law Form 13.1
 * Generated from YAML interview: generated_interviews/form_13.1_interview.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Form 13.1: Form 13.1

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
  'pet_care_pet_care_pet_care_pet': '1000.00',
  'childcare_costs_childcare_cost': '1000.00',
  '_medical_insurance_premiums_an': '1000.00',
  'marriage.date': '2024-01-01',
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
  'daycare_expense_daycare_expens': '1000.00',
  'financial.monthly_expenses': '1000.00',
  'total_amount_of_yearly_expense': '1000.00',
  '23_total_of_debts_and_other_li': '1000.00',
  '1_1_1_1_1_net_partnership_inco': '1000.00',
  '2_2_2_2_2_net_rental_income_gr': '1000.00',
  '6_6_6_6_6_income_from_a_regist': '1000.00',
  '7_7_7_7_7_any_other_income_spe': '1000.00',
  'i_earn_i_earn_per_year_which_s': '1000.00',
  'full_legal_name': 'Test Full legal name',
  'address': 'Test Address',
  '2_2_commissions_tips_and_bonus': '1000.00',
  '4_4_employment_insurance_benef': '1000.00',
  '5_5_workers_compensation_benef': '1000.00',
  '9_9_spousal_support_received_f': '1000.00',
  'field': '1000.00',
  'cpp_contributions_cpp_contribu': '1000.00',
  'ei_premiums_ei_premiums_ei_pre': '1000.00',
  'employee_pension_contributions': '1000.00',
  'union_dues_union_dues_union_du': '1000.00',
  'subtotal_subtotal_subtotal_car': '1000.00',
  'housing_housing_housing_housin': '1000.00',
  'rent_or_mortgage_rent_or_mortg': '1000.00',
  'condominium_fees_condominium_f': '1000.00',
  'repairs_and_maintenance_repair': '1000.00',
  'water_water_water_clothing_clo': '1000.00',
  'heat_heat_heat_hair_care_and_b': '1000.00',
  'electricity_electricity_electr': '1000.00',
  'telephone_telephone_telephone_': '1000.00',
  'cell_phone_cell_phone_cell_pho': '1000.00',
  'cable_cable_cable_cable_cable_': '1000.00',
  'internet_internet_internet_int': '1000.00',
  'groceries_groceries_groceries_': '1000.00',
  'household_supplies_household_s': '1000.00',
  'meals_outside_the_home_meals_o': '1000.00',
  'laundry_and_dry_cleaning_laund': '1000.00',
  'babysitting_costs_babysitting_': '1000.00',
  '6_my_spousepartner_my_spousepa': '1000.00',
  '7_my_spousepartner_or_other_ad': '1000.00',
  '_': '1000.00',
  '15_total_value_of_land_15_tota': '1000.00',
  'household_goods_furniture_hous': '1000.00',
  'cars_boats_vehicles_cars_boats': '1000.00',
  'jewellery_art_electronics_tool': '1000.00',
  'other_special_items_other_spec': '1000.00',
  '16_total_value_of_general_hous': '1000.00',
  '17_total_value_of_accounts_sav': '1000.00',
  '18_total_cash_surrender_value_': '1000.00',
  '19_total_value_of_business_int': '1000.00',
  '20_total_of_money_owed_to_you_': '1000.00',
  'totals_totals_totals_totals_': '1000.00',
  '25_value_of_all_deductions_add': '1000.00',
  'subtract_value_of_all_deductio': '1000.00',
  '3_3_3_3_3_total_amount_of_divi': '1000.00',
  '4_4_4_4_4_total_capital_gains_': '1000.00',
  '5_5_5_5_5_registered_retiremen': '1000.00',
  'subtotal': '1000.00',
  '1. $ $': '1000.00',
  '2. $ $': '1000.00',
  '3. $ $': '1000.00',
  '4. $ $': '1000.00',
  '5. $ $': '1000.00',
  '6. $ $': '1000.00',
  '7. $ $': '1000.00',
  '8. $ $': '1000.00',
  '9. $ $': '1000.00',
  '10. 10. $ $': '1000.00',
  'total_net_annual_amount_total_': '1000.00',
  'total_net_monthly_amount_total': '1000.00',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 13.1 - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
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
    await page.fill('[name="pet_care_pet_care_pet_care_pet"]', testData['pet_care_pet_care_pet_care_pet'] || 'Test Value');
    await page.fill('[name="childcare_costs_childcare_cost"]', testData['childcare_costs_childcare_cost'] || 'Test Value');
    await page.fill('[name="_medical_insurance_premiums_an"]', testData['_medical_insurance_premiums_an'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Marriage Information

    await page.fill('[name="marriage.date"]', testData['marriage.date'] || '2024-01-01');
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
    await page.fill('[name="daycare_expense_daycare_expens"]', testData['daycare_expense_daycare_expens'] || 'Test Value');
    await page.fill('[name="financial.monthly_expenses"]', testData['financial.monthly_expenses'] || 'Test Value');
    await page.fill('[name="total_amount_of_yearly_expense"]', testData['total_amount_of_yearly_expense'] || 'Test Value');
    await page.fill('[name="23_total_of_debts_and_other_li"]', testData['23_total_of_debts_and_other_li'] || 'Test Value');
    await page.fill('[name="1_1_1_1_1_net_partnership_inco"]', testData['1_1_1_1_1_net_partnership_inco'] || 'Test Value');
    await page.fill('[name="2_2_2_2_2_net_rental_income_gr"]', testData['2_2_2_2_2_net_rental_income_gr'] || 'Test Value');
    await page.fill('[name="6_6_6_6_6_income_from_a_regist"]', testData['6_6_6_6_6_income_from_a_regist'] || 'Test Value');
    await page.fill('[name="7_7_7_7_7_any_other_income_spe"]', testData['7_7_7_7_7_any_other_income_spe'] || 'Test Value');
    await page.fill('[name="i_earn_i_earn_per_year_which_s"]', testData['i_earn_i_earn_per_year_which_s'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Additional Information

    await page.fill('[name="full_legal_name"]', testData['full_legal_name'] || 'Test Value');
    await page.fill('[name="address"]', testData['address'] || 'Test Value');
    await page.fill('[name="2_2_commissions_tips_and_bonus"]', testData['2_2_commissions_tips_and_bonus'] || 'Test Value');
    await page.fill('[name="4_4_employment_insurance_benef"]', testData['4_4_employment_insurance_benef'] || 'Test Value');
    await page.fill('[name="5_5_workers_compensation_benef"]', testData['5_5_workers_compensation_benef'] || 'Test Value');
    await page.fill('[name="9_9_spousal_support_received_f"]', testData['9_9_spousal_support_received_f'] || 'Test Value');
    await page.fill('[name="field"]', testData['field'] || 'Test Value');
    await page.fill('[name="cpp_contributions_cpp_contribu"]', testData['cpp_contributions_cpp_contribu'] || 'Test Value');
    await page.fill('[name="ei_premiums_ei_premiums_ei_pre"]', testData['ei_premiums_ei_premiums_ei_pre'] || 'Test Value');
    await page.fill('[name="employee_pension_contributions"]', testData['employee_pension_contributions'] || 'Test Value');
    await page.fill('[name="union_dues_union_dues_union_du"]', testData['union_dues_union_dues_union_du'] || 'Test Value');
    await page.fill('[name="subtotal_subtotal_subtotal_car"]', testData['subtotal_subtotal_subtotal_car'] || 'Test Value');
    await page.fill('[name="housing_housing_housing_housin"]', testData['housing_housing_housing_housin'] || 'Test Value');
    await page.fill('[name="rent_or_mortgage_rent_or_mortg"]', testData['rent_or_mortgage_rent_or_mortg'] || 'Test Value');
    await page.fill('[name="condominium_fees_condominium_f"]', testData['condominium_fees_condominium_f'] || 'Test Value');
    await page.fill('[name="repairs_and_maintenance_repair"]', testData['repairs_and_maintenance_repair'] || 'Test Value');
    await page.fill('[name="subtotal_subtotal_subtotal_sub"]', testData['subtotal_subtotal_subtotal_sub'] || 'Test Value');
    await page.fill('[name="water_water_water_clothing_clo"]', testData['water_water_water_clothing_clo'] || 'Test Value');
    await page.fill('[name="heat_heat_heat_hair_care_and_b"]', testData['heat_heat_heat_hair_care_and_b'] || 'Test Value');
    await page.fill('[name="electricity_electricity_electr"]', testData['electricity_electricity_electr'] || 'Test Value');
    await page.fill('[name="telephone_telephone_telephone_"]', testData['telephone_telephone_telephone_'] || 'Test Value');
    await page.fill('[name="cell_phone_cell_phone_cell_pho"]', testData['cell_phone_cell_phone_cell_pho'] || 'Test Value');
    await page.fill('[name="cable_cable_cable_cable_cable_"]', testData['cable_cable_cable_cable_cable_'] || 'Test Value');
    await page.fill('[name="internet_internet_internet_int"]', testData['internet_internet_internet_int'] || 'Test Value');
    await page.fill('[name="groceries_groceries_groceries_"]', testData['groceries_groceries_groceries_'] || 'Test Value');
    await page.fill('[name="household_supplies_household_s"]', testData['household_supplies_household_s'] || 'Test Value');
    await page.fill('[name="meals_outside_the_home_meals_o"]', testData['meals_outside_the_home_meals_o'] || 'Test Value');
    await page.fill('[name="laundry_and_dry_cleaning_laund"]', testData['laundry_and_dry_cleaning_laund'] || 'Test Value');
    await page.fill('[name="babysitting_costs_babysitting_"]', testData['babysitting_costs_babysitting_'] || 'Test Value');
    await page.fill('[name="6_my_spousepartner_my_spousepa"]', testData['6_my_spousepartner_my_spousepa'] || 'Test Value');
    await page.fill('[name="7_my_spousepartner_or_other_ad"]', testData['7_my_spousepartner_or_other_ad'] || 'Test Value');
    await page.fill('[name="_"]', testData['_'] || 'Test Value');
    await page.fill('[name="15_total_value_of_land_15_tota"]', testData['15_total_value_of_land_15_tota'] || 'Test Value');
    await page.fill('[name="household_goods_furniture_hous"]', testData['household_goods_furniture_hous'] || 'Test Value');
    await page.fill('[name="cars_boats_vehicles_cars_boats"]', testData['cars_boats_vehicles_cars_boats'] || 'Test Value');
    await page.fill('[name="jewellery_art_electronics_tool"]', testData['jewellery_art_electronics_tool'] || 'Test Value');
    await page.fill('[name="other_special_items_other_spec"]', testData['other_special_items_other_spec'] || 'Test Value');
    await page.fill('[name="16_total_value_of_general_hous"]', testData['16_total_value_of_general_hous'] || 'Test Value');
    await page.fill('[name="17_total_value_of_accounts_sav"]', testData['17_total_value_of_accounts_sav'] || 'Test Value');
    await page.fill('[name="18_total_cash_surrender_value_"]', testData['18_total_cash_surrender_value_'] || 'Test Value');
    await page.fill('[name="19_total_value_of_business_int"]', testData['19_total_value_of_business_int'] || 'Test Value');
    await page.fill('[name="20_total_of_money_owed_to_you_"]', testData['20_total_of_money_owed_to_you_'] || 'Test Value');
    await page.fill('[name="totals_totals_totals_totals_"]', testData['totals_totals_totals_totals_'] || 'Test Value');
    await page.fill('[name="25_value_of_all_deductions_add"]', testData['25_value_of_all_deductions_add'] || 'Test Value');
    await page.fill('[name="subtract_value_of_all_deductio"]', testData['subtract_value_of_all_deductio'] || 'Test Value');
    await page.fill('[name="3_3_3_3_3_total_amount_of_divi"]', testData['3_3_3_3_3_total_amount_of_divi'] || 'Test Value');
    await page.fill('[name="4_4_4_4_4_total_capital_gains_"]', testData['4_4_4_4_4_total_capital_gains_'] || 'Test Value');
    await page.fill('[name="5_5_5_5_5_registered_retiremen"]', testData['5_5_5_5_5_registered_retiremen'] || 'Test Value');
    await page.fill('[name="subtotal"]', testData['subtotal'] || 'Test Value');
    // TODO: Fill field 1 (type: currency)
    // TODO: Fill field 2 (type: currency)
    // TODO: Fill field 3 (type: currency)
    // TODO: Fill field 4 (type: currency)
    // TODO: Fill field 5 (type: currency)
    // TODO: Fill field 6 (type: currency)
    // TODO: Fill field 7 (type: currency)
    // TODO: Fill field 8 (type: currency)
    // TODO: Fill field 9 (type: currency)
    // TODO: Fill field 1010 (type: currency)
    await page.fill('[name="total_net_annual_amount_total_"]', testData['total_net_annual_amount_total_'] || 'Test Value');
    await page.fill('[name="total_net_monthly_amount_total"]', testData['total_net_monthly_amount_total'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 13.1 - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

});

test.describe('Form 13.1 - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
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
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
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

test.describe('Form 13.1 - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
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
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    
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
test.describe('Form 13.1 - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13.1.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 13.1 loaded in ${loadTime}ms`);
  });
});
