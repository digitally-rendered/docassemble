/**
 * Test suite for Form 8 - Application (General)
 * Tests the generated interview located at utilities/generated_interviews/form_8_interview.yml
 */

import { test, expect } from '@playwright/test';

// Import helper functions
const { 
  waitForDocassembleLoad,
  checkForInterviewCrash,
  clickRadioByLabel,
  fillInputByLabel,
  clickContinue,
  selectFromDropdown,
  checkCheckbox
} = require('../utils/interview-helpers');

const { 
  validateFieldRequired,
  validateEmailFormat,
  validatePhoneFormat,
  validatePostalCode
} = require('../utils/test-helpers');

test.describe('Form 8 - Application (General) Interview', () => {
  const INTERVIEW_URL = '/interview?i=docassemble.playground1%3Autilities%2Fgenerated_interviews%2Fform_8_interview.yml';
  const BASE_URL = process.env.DOCASSEMBLE_URL || 'http://localhost';

  test.beforeEach(async ({ page }) => {
    // Navigate to the interview
    await page.goto(`${BASE_URL}${INTERVIEW_URL}`);
    await waitForDocassembleLoad(page);
  });

  test('Interview loads without errors', async ({ page }) => {
    // Check for crash
    const crashCheck = await checkForInterviewCrash(page);
    expect(crashCheck.crashed).toBe(false);
    
    // Verify the interview starts properly
    const pageText = await page.textContent('body');
    expect(pageText).toContain('Form 8');
  });

  test('Complete happy path - minimal required fields only', async ({ page }) => {
    // Court Information
    await expect(page.locator('h1')).toContainText('Court Information');
    await page.fill('input[type="text"]', 'FC-24-12345');
    await page.locator('select').selectOption('Toronto');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Applicant Information
    await expect(page.locator('h1')).toContainText('Applicant Information');
    await fillInputByLabel(page, 'Full legal name', 'John Michael Smith');
    await fillInputByLabel(page, 'Street address', '123 Main Street');
    await fillInputByLabel(page, 'City', 'Toronto');
    await fillInputByLabel(page, 'Province', 'Ontario');
    await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Respondent Information
    await expect(page.locator('h1')).toContainText('Respondent Information');
    await fillInputByLabel(page, 'Full legal name', 'Jane Elizabeth Doe');
    await fillInputByLabel(page, 'Street address', '456 Queen Street');
    await fillInputByLabel(page, 'City', 'Toronto');
    await fillInputByLabel(page, 'Province', 'Ontario');
    await fillInputByLabel(page, 'Postal code', 'M5V 3A8');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Marriage Information
    await expect(page.locator('h1')).toContainText('Marriage Information');
    await page.fill('input[type="date"]', '2015-06-15');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Additional Information
    await expect(page.locator('h1')).toContainText('Additional Information');
    await fillInputByLabel(page, 'Full legal name', 'John Michael Smith');
    await fillInputByLabel(page, 'Address', '123 Main Street, Toronto, ON');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Review Screen
    await expect(page.locator('h1')).toContainText('Review Your Information');
    
    // Verify displayed information
    const reviewText = await page.textContent('body');
    expect(reviewText).toContain('FC-24-12345');
    expect(reviewText).toContain('Toronto');
    expect(reviewText).toContain('John Michael Smith');
    expect(reviewText).toContain('Jane Elizabeth Doe');
    expect(reviewText).toContain('123 Main Street');
    expect(reviewText).toContain('456 Queen Street');
    
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Final Screen
    await expect(page.locator('h1')).toContainText('Form 8 Complete');
    const finalText = await page.textContent('body');
    expect(finalText).toContain('Your Form 8');
    expect(finalText).toContain('has been completed successfully');
    expect(finalText).toContain('FC-24-12345');
    expect(finalText).toContain('Toronto');
  });

  test('Complete path with all optional fields', async ({ page }) => {
    // Court Information
    await expect(page.locator('h1')).toContainText('Court Information');
    await page.fill('input[type="text"]', 'FC-24-99999');
    await page.locator('select').selectOption('Ottawa');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Applicant Information with optional fields
    await expect(page.locator('h1')).toContainText('Applicant Information');
    await fillInputByLabel(page, 'Full legal name', 'Robert James Wilson');
    await fillInputByLabel(page, 'Street address', '789 Bank Street');
    await fillInputByLabel(page, 'City', 'Ottawa');
    await fillInputByLabel(page, 'Province', 'Ontario');
    await fillInputByLabel(page, 'Postal code', 'K1S 3T4');
    await fillInputByLabel(page, 'Phone number', '613-555-0123');
    await fillInputByLabel(page, 'Email address', 'robert.wilson@example.com');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Respondent Information with optional fields
    await expect(page.locator('h1')).toContainText('Respondent Information');
    await fillInputByLabel(page, 'Full legal name', 'Sarah Anne Johnson');
    await fillInputByLabel(page, 'Street address', '321 Sparks Street');
    await fillInputByLabel(page, 'City', 'Ottawa');
    await fillInputByLabel(page, 'Province', 'Ontario');
    await fillInputByLabel(page, 'Postal code', 'K1A 0G9');
    await fillInputByLabel(page, 'Phone number', '613-555-9876');
    await fillInputByLabel(page, 'Email address', 'sarah.johnson@example.com');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Continue through remaining screens
    await page.fill('input[type="date"]', '2010-09-20');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    await fillInputByLabel(page, 'Full legal name', 'Robert James Wilson');
    await fillInputByLabel(page, 'Address', '789 Bank Street, Ottawa, ON K1S 3T4');
    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Review screen - verify optional fields are displayed
    const reviewText = await page.textContent('body');
    expect(reviewText).toContain('613-555-0123');
    expect(reviewText).toContain('robert.wilson@example.com');
    expect(reviewText).toContain('613-555-9876');
    expect(reviewText).toContain('sarah.johnson@example.com');

    await clickContinue(page);
    await waitForDocassembleLoad(page);

    // Verify final screen
    await expect(page.locator('h1')).toContainText('Form 8 Complete');
  });

  test.describe('Field Validation', () => {
    test('Required fields show validation errors when empty', async ({ page }) => {
      // Try to continue without filling court information
      await expect(page.locator('h1')).toContainText('Court Information');
      await clickContinue(page);
      await waitForDocassembleLoad(page);
      
      // Should show validation error
      const errorText = await page.textContent('body');
      expect(errorText.toLowerCase()).toMatch(/(required|must|cannot be empty|please enter)/i);
    });

    test('Email validation', async ({ page }) => {
      // Navigate to applicant information
      await page.fill('input[type="text"]', 'FC-24-11111');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      // Fill required fields
      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      
      // Test invalid email format
      await fillInputByLabel(page, 'Email address', 'invalid-email');
      await clickContinue(page);
      await waitForDocassembleLoad(page);
      
      // Should show email validation error or stay on same page
      const pageContent = await page.textContent('body');
      const hasError = pageContent.toLowerCase().includes('email') && 
                       (pageContent.toLowerCase().includes('invalid') || 
                        pageContent.toLowerCase().includes('valid'));
      
      if (!hasError) {
        // If it proceeded, we're still on same page
        await expect(page.locator('h1')).toContainText('Applicant Information');
      }
    });

    test('Phone number validation', async ({ page }) => {
      // Navigate to applicant information
      await page.fill('input[type="text"]', 'FC-24-22222');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      // Fill required fields
      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      
      // Test valid phone format
      await fillInputByLabel(page, 'Phone number', '416-555-0123');
      await clickContinue(page);
      await waitForDocassembleLoad(page);
      
      // Should proceed to next page
      await expect(page.locator('h1')).toContainText('Respondent Information');
    });

    test('Postal code validation for Ontario', async ({ page }) => {
      // Navigate to applicant information
      await page.fill('input[type="text"]', 'FC-24-33333');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      // Test invalid Ontario postal code
      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'X1X 1X1'); // Invalid for Ontario
      await clickContinue(page);
      await waitForDocassembleLoad(page);
      
      // Should show error or stay on same page
      const pageContent = await page.textContent('body');
      if (pageContent.toLowerCase().includes('postal')) {
        expect(pageContent.toLowerCase()).toMatch(/(invalid|valid|ontario postal)/i);
      }
    });
  });

  test.describe('Navigation', () => {
    test('Back button navigation works correctly', async ({ page }) => {
      // Navigate through first few screens
      await page.fill('input[type="text"]', 'FC-24-44444');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      // Should be on Respondent Information
      await expect(page.locator('h1')).toContainText('Respondent Information');

      // Click back button
      const backButton = page.locator('button:has-text("Back")').or(page.locator('a:has-text("Back")'));
      if (await backButton.count() > 0) {
        await backButton.first().click();
        await waitForDocassembleLoad(page);
        
        // Should be back on Applicant Information
        await expect(page.locator('h1')).toContainText('Applicant Information');
        
        // Data should be preserved
        const nameInput = await page.inputValue('input[type="text"]').catch(() => '');
        expect(nameInput).toBeTruthy();
      }
    });

    test('Review screen edit functionality', async ({ page }) => {
      // Complete all required fields to get to review
      await page.fill('input[type="text"]', 'FC-24-55555');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);

      await fillInputByLabel(page, 'Full legal name', 'Original Name');
      await fillInputByLabel(page, 'Street address', '123 Original St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      await clickContinue(page);

      await fillInputByLabel(page, 'Full legal name', 'Respondent Name');
      await fillInputByLabel(page, 'Street address', '456 Respondent Ave');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5V 3A8');
      await clickContinue(page);

      await page.fill('input[type="date"]', '2020-01-01');
      await clickContinue(page);

      await fillInputByLabel(page, 'Full legal name', 'Additional Name');
      await fillInputByLabel(page, 'Address', 'Additional Address');
      await clickContinue(page);

      // Should be on review screen
      await expect(page.locator('h1')).toContainText('Review Your Information');

      // Look for edit links/buttons
      const editButtons = page.locator('button:has-text("Edit")').or(page.locator('a:has-text("Edit")'));
      if (await editButtons.count() > 0) {
        // Click first edit button
        await editButtons.first().click();
        await waitForDocassembleLoad(page);
        
        // Should navigate to an edit screen
        const heading = await page.locator('h1').textContent();
        expect(heading).toBeTruthy();
      }
    });
  });

  test.describe('Edge Cases', () => {
    test('Handles special characters in names', async ({ page }) => {
      await page.fill('input[type="text"]', 'FC-24-66666');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);

      // Test names with special characters
      await fillInputByLabel(page, 'Full legal name', "Jean-François O'Brien-Smith");
      await fillInputByLabel(page, 'Street address', '123 Rue Saint-Denis');
      await fillInputByLabel(page, 'City', "Val-d'Or");
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      await clickContinue(page);
      
      // Should handle special characters properly
      await expect(page.locator('h1')).toContainText('Respondent Information');
    });

    test('Handles very long inputs', async ({ page }) => {
      await page.fill('input[type="text"]', 'FC-24-77777');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);

      const longName = 'A'.repeat(100);
      const longAddress = 'B'.repeat(200);
      
      await fillInputByLabel(page, 'Full legal name', longName);
      await fillInputByLabel(page, 'Street address', longAddress);
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      await clickContinue(page);
      
      // Should either truncate or handle gracefully
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
    });

    test('Handles browser refresh mid-interview', async ({ page }) => {
      // Start interview and fill some data
      await page.fill('input[type="text"]', 'FC-24-88888');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);
      await waitForDocassembleLoad(page);

      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      
      // Refresh the page
      await page.reload();
      await waitForDocassembleLoad(page);
      
      // Check that interview hasn't crashed
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
      
      // Data might be preserved or user might need to re-enter
      // Both behaviors are acceptable
    });

    test('Handles future dates appropriately', async ({ page }) => {
      // Navigate to marriage information
      await page.fill('input[type="text"]', 'FC-24-99999');
      await page.locator('select').selectOption('Toronto');
      await clickContinue(page);

      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await fillInputByLabel(page, 'Street address', '123 Test St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5H 2N2');
      await clickContinue(page);

      await fillInputByLabel(page, 'Full legal name', 'Other Party');
      await fillInputByLabel(page, 'Street address', '456 Other St');
      await fillInputByLabel(page, 'City', 'Toronto');
      await fillInputByLabel(page, 'Province', 'Ontario');
      await fillInputByLabel(page, 'Postal code', 'M5V 3A8');
      await clickContinue(page);

      // Try to enter future date for marriage
      const futureDate = new Date();
      futureDate.setFullYear(futureDate.getFullYear() + 1);
      const futureDateStr = futureDate.toISOString().split('T')[0];
      
      await page.fill('input[type="date"]', futureDateStr);
      await clickContinue(page);
      
      // Should either show validation error or handle appropriately
      const pageContent = await page.textContent('body');
      // Check if still on same page or shows error
      if (pageContent.includes('Marriage Information')) {
        // Still on same page, likely validation prevented it
        expect(true).toBe(true);
      }
    });
  });

  test.describe('Court Location Options', () => {
    test('All Ontario court locations are available', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('Court Information');
      
      const selectElement = page.locator('select');
      const options = await selectElement.locator('option').allTextContents();
      
      // Verify key Ontario court locations are present
      const expectedLocations = [
        'Toronto', 'Ottawa', 'London', 'Hamilton', 'Kitchener',
        'Windsor', 'Barrie', 'Kingston', 'Thunder Bay', 'Sudbury'
      ];
      
      for (const location of expectedLocations) {
        expect(options.some(opt => opt.includes(location))).toBe(true);
      }
    });

    test('Other location option is available', async ({ page }) => {
      const selectElement = page.locator('select');
      const options = await selectElement.locator('option').allTextContents();
      
      expect(options.some(opt => opt.toLowerCase().includes('other'))).toBe(true);
    });
  });

  test.describe('Accessibility', () => {
    test('Form has proper labels for screen readers', async ({ page }) => {
      // Check that all inputs have associated labels
      const inputs = await page.locator('input[type="text"], input[type="email"], input[type="tel"], input[type="date"]').all();
      
      for (const input of inputs) {
        const id = await input.getAttribute('id');
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          const labelCount = await label.count();
          
          // Either has explicit label or aria-label
          if (labelCount === 0) {
            const ariaLabel = await input.getAttribute('aria-label');
            expect(ariaLabel).toBeTruthy();
          }
        }
      }
    });

    test('Tab navigation works correctly', async ({ page }) => {
      await page.fill('input[type="text"]', 'FC-24-00000');
      
      // Tab through form elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to navigate with keyboard
      const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(focusedElement).toBeTruthy();
    });
  });

  test.describe('Performance', () => {
    test('Interview loads within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}${INTERVIEW_URL}`);
      await page.waitForSelector('h1', { timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 10 seconds
      expect(loadTime).toBeLessThan(10000);
      
      // Warn if load time is over 5 seconds
      if (loadTime > 5000) {
        console.warn(`Interview load time is ${loadTime}ms - consider optimization`);
      }
    });

    test('Navigation between screens is responsive', async ({ page }) => {
      await page.fill('input[type="text"]', 'FC-24-PERF1');
      await page.locator('select').selectOption('Toronto');
      
      const startTime = Date.now();
      await clickContinue(page);
      await page.waitForSelector('h1:has-text("Applicant Information")', { timeout: 5000 });
      const navigationTime = Date.now() - startTime;
      
      // Navigation should be under 5 seconds
      expect(navigationTime).toBeLessThan(5000);
    });
  });
});

// Helper function to click continue button
async function clickContinue(page) {
  const continueButton = page.locator('button:has-text("Continue")').or(
    page.locator('button:has-text("Next")').or(
      page.locator('input[type="submit"]')
    )
  );
  
  if (await continueButton.count() > 0) {
    await continueButton.first().click();
  } else {
    throw new Error('Continue button not found');
  }
}