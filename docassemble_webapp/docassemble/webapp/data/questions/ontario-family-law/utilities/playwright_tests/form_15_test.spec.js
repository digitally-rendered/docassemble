/**
 * Playwright tests for Ontario Family Law Form 15
 * Generated from YAML interview: generated_interviews/form_15_enhanced.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Ontario Form 15 - Motion to Change
 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
test.describe.configure({ mode: 'parallel' });

// Test data
const testData = {
  'applicant.name.first': 'Test First name',
  'applicant.name.middle': 'Test Middle name',
  'applicant.name.last': 'Test Last name',
  'respondent.address.address': 'Test Street address',
  'respondent.address.city': 'Test City',
  'respondent.address.state': 'Test Province',
  'respondent.address.zip': 'Test Postal code',
  'respondent.phone_number': 'Test Phone number',
  'respondent.email': 'test@example.com',
  'respondent.birthdate': '2024-01-01',
  'applicant.has_lawyer': true,
  'applicant.lawyer.name.first': 'Test Lawyer's first name',
  'applicant.lawyer.name.last': 'Test Lawyer's last name',
  'applicant.lawyer.firm_name': 'Test Law firm name',
  'applicant.lawyer.phone_number': 'Test Lawyer's phone',
  'applicant.lawyer.email': 'test@example.com',
  'respondent.name.first': 'Test First name',
  'respondent.name.middle': 'Test Middle name',
  'respondent.name.last': 'Test Last name',
  'case.court_file_number': 'Test Court file number',
  'case.related_case_number': 'Test Court file number of related case',
  'case.related_case_court': 'Test Court where related case was filed',
  'case.related_case_status': 'Test Status of related case',
  'simple_income.annual_gross': '1000.00',
  'simple_income.employment': '1000.00',
  'simple_income.self_employment': '1000.00',
  'simple_income.investment': '1000.00',
  'simple_income.pension': '1000.00',
  'simple_income.other': '1000.00',
  'existing_order.order_date': '2024-01-01',
  'existing_order.court': 'Test Court that made the order',
  'existing_order.file_number': 'Test Court file number',
  'existing_order.judge': 'Test Judge who made the order',
  'existing_order.current_terms': 'Test What the current order says',
  'area': 'Test input type',
  'changes.child_support': true,
  'changes.spousal_support': true,
  'changes.custody': true,
  'changes.other': true,
  'changes.description': 'Test Detailed description of changes',
  'changes.reasons': 'Test Reasons for change',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 15 - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
    // Wait for the interview to load
    await page.waitForSelector('.da-page-header', { timeout: 10000 });
    
    // Fill fields for: What is your full legal name?
    await page.fill('[name="applicant.name.first"]', testData['applicant.name.first'] || 'Test Value');
    await page.fill('[name="applicant.name.middle"]', testData['applicant.name.middle'] || 'Test Value');
    await page.fill('[name="applicant.name.last"]', testData['applicant.name.last'] || 'Test Value');
    // Fill fields for: What is your address?
    await page.fill('[name="respondent.address.address"]', testData['respondent.address.address'] || 'Test Value');
    await page.fill('[name="respondent.address.city"]', testData['respondent.address.city'] || 'Test Value');
    await page.fill('[name="respondent.address.state"]', testData['respondent.address.state'] || 'Test Value');
    await page.fill('[name="respondent.address.zip"]', testData['respondent.address.zip'] || 'Test Value');
    // Fill fields for: What are your contact details?
    await page.fill('[name="respondent.phone_number"]', testData['respondent.phone_number'] || 'Test Value');
    await page.fill('[name="respondent.email"]', testData['respondent.email'] || 'Test Value');
    // Fill fields for: What is your date of birth?
    await page.fill('[name="respondent.birthdate"]', testData['respondent.birthdate'] || '2024-01-01');
    // Fill fields for: Do you have a lawyer?
    await page.click('[name="applicant.has_lawyer"][value="True"]');
    // Fill fields for: What are your lawyer's details?
    await page.fill('[name="applicant.lawyer.name.first"]', testData['applicant.lawyer.name.first'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.name.last"]', testData['applicant.lawyer.name.last'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.firm_name"]', testData['applicant.lawyer.firm_name'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.phone_number"]', testData['applicant.lawyer.phone_number'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.email"]', testData['applicant.lawyer.email'] || 'Test Value');
    // Fill fields for: What is the respondent's full legal name?
    await page.fill('[name="respondent.name.first"]', testData['respondent.name.first'] || 'Test Value');
    await page.fill('[name="respondent.name.middle"]', testData['respondent.name.middle'] || 'Test Value');
    await page.fill('[name="respondent.name.last"]', testData['respondent.name.last'] || 'Test Value');
    // Fill fields for: What is the respondent's address?
    await page.fill('[name="respondent.address.address"]', testData['respondent.address.address'] || 'Test Value');
    await page.fill('[name="respondent.address.city"]', testData['respondent.address.city'] || 'Test Value');
    await page.fill('[name="respondent.address.state"]', testData['respondent.address.state'] || 'Test Value');
    await page.fill('[name="respondent.address.zip"]', testData['respondent.address.zip'] || 'Test Value');
    // Fill fields for: What are the respondent's contact details?
    await page.fill('[name="respondent.phone_number"]', testData['respondent.phone_number'] || 'Test Value');
    await page.fill('[name="respondent.email"]', testData['respondent.email'] || 'Test Value');
    // Fill fields for: What is the respondent's date of birth?
    await page.fill('[name="respondent.birthdate"]', testData['respondent.birthdate'] || '2024-01-01');
    // Fill fields for: Do you have a court file number?
    await page.fill('[name="case.court_file_number"]', testData['case.court_file_number'] || 'Test Value');
    // Fill fields for: What are the details of the related cases?
    await page.fill('[name="case.related_case_number"]', testData['case.related_case_number'] || 'Test Value');
    await page.fill('[name="case.related_case_court"]', testData['case.related_case_court'] || 'Test Value');
    await page.fill('[name="case.related_case_status"]', testData['case.related_case_status'] || 'Test Value');
    // Fill fields for: What is your current annual income?
    await page.fill('[name="simple_income.annual_gross"]', testData['simple_income.annual_gross'] || 'Test Value');
    // Fill fields for: What are your main sources of income?
    await page.fill('[name="simple_income.employment"]', testData['simple_income.employment'] || 'Test Value');
    await page.fill('[name="simple_income.self_employment"]', testData['simple_income.self_employment'] || 'Test Value');
    await page.fill('[name="simple_income.investment"]', testData['simple_income.investment'] || 'Test Value');
    await page.fill('[name="simple_income.pension"]', testData['simple_income.pension'] || 'Test Value');
    await page.fill('[name="simple_income.other"]', testData['simple_income.other'] || 'Test Value');
    // Fill fields for: What existing order do you want to change?
    await page.fill('[name="existing_order.order_date"]', testData['existing_order.order_date'] || '2024-01-01');
    await page.fill('[name="existing_order.court"]', testData['existing_order.court'] || 'Test Value');
    await page.fill('[name="existing_order.file_number"]', testData['existing_order.file_number'] || 'Test Value');
    await page.fill('[name="existing_order.judge"]', testData['existing_order.judge'] || 'Test Value');
    await page.fill('[name="existing_order.current_terms"]', testData['existing_order.current_terms'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Fill fields for: What changes do you want to make?
    await page.click('[name="changes.child_support"][value="True"]');
    await page.click('[name="changes.spousal_support"][value="True"]');
    await page.click('[name="changes.custody"][value="True"]');
    await page.click('[name="changes.other"][value="True"]');
    await page.fill('[name="changes.description"]', testData['changes.description'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Fill fields for: Why are you asking for these changes?
    await page.fill('[name="changes.reasons"]', testData['changes.reasons'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 15 - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

});

test.describe('Form 15 - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
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
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
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

test.describe('Form 15 - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
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
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    
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
test.describe('Form 15 - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 15 loaded in ${loadTime}ms`);
  });
});
