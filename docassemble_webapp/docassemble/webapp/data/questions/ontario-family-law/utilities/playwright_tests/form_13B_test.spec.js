/**
 * Playwright tests for Ontario Family Law Form 13B
 * Generated from YAML interview: generated_interviews/form_13B_interview.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Form 13B: Form 13B

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
  'total_of_debt_items_total_of_d': '1000.00',
  'total_of_property_items_total_': '1000.00',
  '1. $ $': '1000.00',
  '_': '1000.00',
  'total_1_': '1000.00',
  '1. 1. $ $ $ $': '1000.00',
  'total_2_total_2_': '1000.00',
  'net_total_3_3a_minus_3b_net_to': '1000.00',
  'total_4_': '1000.00',
  'total_2_from_page_2_': '1000.00',
  'total_3_from_page_2_': '1000.00',
  'total_4_from_page_3_': '1000.00',
  'total_5_total_2_total_3_total_': '1000.00',
  'total_1_from_page_1_': '1000.00',
  'total_5_from_above_': '1000.00',
  'total_6': '1000.00',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 13B - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
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

    await page.fill('[name="total_of_debt_items_total_of_d"]', testData['total_of_debt_items_total_of_d'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Property Information

    await page.fill('[name="total_of_property_items_total_"]', testData['total_of_property_items_total_'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Fill fields for: Additional Information

    // TODO: Fill field 1 (type: currency)
    await page.fill('[name="_"]', testData['_'] || 'Test Value');
    await page.fill('[name="total_1_"]', testData['total_1_'] || 'Test Value');
    // TODO: Fill field 11 (type: currency)
    await page.fill('[name="total_2_total_2_"]', testData['total_2_total_2_'] || 'Test Value');
    await page.fill('[name="net_total_3_3a_minus_3b_net_to"]', testData['net_total_3_3a_minus_3b_net_to'] || 'Test Value');
    await page.fill('[name="total_4_"]', testData['total_4_'] || 'Test Value');
    await page.fill('[name="total_2_from_page_2_"]', testData['total_2_from_page_2_'] || 'Test Value');
    await page.fill('[name="total_3_from_page_2_"]', testData['total_3_from_page_2_'] || 'Test Value');
    await page.fill('[name="total_4_from_page_3_"]', testData['total_4_from_page_3_'] || 'Test Value');
    await page.fill('[name="total_5_total_2_total_3_total_"]', testData['total_5_total_2_total_3_total_'] || 'Test Value');
    await page.fill('[name="total_1_from_page_1_"]', testData['total_1_from_page_1_'] || 'Test Value');
    await page.fill('[name="total_5_from_above_"]', testData['total_5_from_above_'] || 'Test Value');
    await page.fill('[name="total_6"]', testData['total_6'] || 'Test Value');
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');

    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 13B - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate phone number fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
    // Test invalid phone
    await page.fill('[type="tel"]', '123');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

  test('Validate required fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
    // Try to continue without filling required fields
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-required')).toBeVisible();
  });

});

test.describe('Form 13B - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
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
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
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

test.describe('Form 13B - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
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
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    
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
test.describe('Form 13B - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_13B.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 13B loaded in ${loadTime}ms`);
  });
});
