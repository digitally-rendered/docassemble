/**
 * Playwright tests for Ontario Family Law Form 15C
 * Generated from YAML interview: generated_interviews/form_15C_interview.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Form 15C: Form 15C

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
  'based_on_the_payors_annual_inc': '1000.00',
  'full_legal_name': 'Test Full legal name',
  'address': 'Test Address',
  'shall_pay_to_name_of_party_sha': '1000.00',
  'shall_pay_name_of_party_shall_': '1000.00',
  '_': '1000.00',
  'fixed_at_fixed_at_fixed_at_fix': '2024-01-01',
  '_per_month_with_payments_to_be': '2024-01-01',
  'shall_be_fixed_at_shall_be_fix': '2024-01-01',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 15C - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
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

    // Fill fields for: Financial Information

    await page.fill('[name="based_on_the_payors_annual_inc"]', testData['based_on_the_payors_annual_inc'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Additional Information

    await page.fill('[name="full_legal_name"]', testData['full_legal_name'] || 'Test Value');
    await page.fill('[name="address"]', testData['address'] || 'Test Value');
    await page.fill('[name="shall_pay_to_name_of_party_sha"]', testData['shall_pay_to_name_of_party_sha'] || 'Test Value');
    await page.fill('[name="shall_pay_name_of_party_shall_"]', testData['shall_pay_name_of_party_shall_'] || 'Test Value');
    await page.fill('[name="_"]', testData['_'] || 'Test Value');
    await page.fill('[name="fixed_at_fixed_at_fixed_at_fix"]', testData['fixed_at_fixed_at_fixed_at_fix'] || '2024-01-01');
    await page.fill('[name="_per_month_with_payments_to_be"]', testData['_per_month_with_payments_to_be'] || '2024-01-01');
    await page.fill('[name="shall_be_fixed_at_shall_be_fix"]', testData['shall_be_fixed_at_shall_be_fix'] || '2024-01-01');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 15C - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

});

test.describe('Form 15C - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
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
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
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

test.describe('Form 15C - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
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
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    
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
test.describe('Form 15C - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_15C.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 15C loaded in ${loadTime}ms`);
  });
});
