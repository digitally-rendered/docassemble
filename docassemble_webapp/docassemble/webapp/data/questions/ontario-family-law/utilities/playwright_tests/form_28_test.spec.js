/**
 * Playwright tests for Ontario Family Law Form 28
 * Generated from YAML interview: generated_interviews/form_28_interview.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Form 28: Form 28

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
  'insert_amount_to_be_realized_f': '2024-01-01',
  'priority_for_support_payments': '1000.00',
  'assignment_of_costs_to_legal_a': '1000.00',
  'fine_bond_or_recognizance_fine': '1000.00',
  'field': '1000.00',
  '_at_at_at_name_address_telepho': '1000.00',
  '_writ_of_seizure_and_sale_writ': '1000.00',
  '_note': '2024-01-01',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 28 - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
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

    // Fill fields for: Additional Information

    await page.fill('[name="insert_amount_to_be_realized_f"]', testData['insert_amount_to_be_realized_f'] || '2024-01-01');
    await page.fill('[name="priority_for_support_payments"]', testData['priority_for_support_payments'] || 'Test Value');
    await page.fill('[name="assignment_of_costs_to_legal_a"]', testData['assignment_of_costs_to_legal_a'] || 'Test Value');
    await page.fill('[name="fine_bond_or_recognizance_fine"]', testData['fine_bond_or_recognizance_fine'] || 'Test Value');
    await page.fill('[name="field"]', testData['field'] || 'Test Value');
    await page.fill('[name="_at_at_at_name_address_telepho"]', testData['_at_at_at_name_address_telepho'] || 'Test Value');
    await page.fill('[name="_writ_of_seizure_and_sale_writ"]', testData['_writ_of_seizure_and_sale_writ'] || 'Test Value');
    await page.fill('[name="_note"]', testData['_note'] || '2024-01-01');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 28 - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

});

test.describe('Form 28 - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
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
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
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

test.describe('Form 28 - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
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
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    
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
test.describe('Form 28 - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_28.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 28 loaded in ${loadTime}ms`);
  });
});
