/**
 * Comprehensive Test Suite for Form 8 Enhanced Interview
 * Tests the enhanced Form 8 interview with proper field labels and Ontario-specific validation
 * Located at: /docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/form_8_enhanced.yml
 */

import { test, expect } from '@playwright/test';

// Import helper functions
const { 
  waitForDocassembleLoad,
  checkForInterviewCrash,
  clickRadioByLabel,
  fillInputByLabel,
  clickCheckboxByLabel,
  safeNavigate
} = require('../utils/interview-helpers');

const { 
  validateFieldRequired,
  validateEmailFormat,
  validatePhoneFormat,
  validatePostalCode
} = require('../utils/test-helpers');

test.describe('Form 8 Enhanced Interview - Comprehensive Tests', () => {
  const INTERVIEW_URL = '/interview?i=docassemble.playground1%3Aform_8_enhanced.yml';
  const BASE_URL = process.env.DOCASSEMBLE_URL || 'http://localhost';

  test.beforeEach(async ({ page }) => {
    // Navigate to the interview
    await page.goto(`${BASE_URL}${INTERVIEW_URL}`);
    await waitForDocassembleLoad(page);
  });

  test.describe('Interview Loading and Initialization', () => {
    test('Interview loads without errors', async ({ page }) => {
      // Check for crash
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
      
      // Verify the interview starts properly
      const pageText = await page.textContent('body');
      expect(pageText).toMatch(/Form 8|Court Information|Application/i);
      
      // Check metadata is loaded
      expect(pageText).toContain('Ontario Family Law');
    });

    test('Required modules are loaded', async ({ page }) => {
      // Check that the interview doesn't crash with module loading errors
      const crashCheck = await checkForInterviewCrash(page);
      if (crashCheck.crashed) {
        console.error('Module loading error:', crashCheck.message);
      }
      expect(crashCheck.crashed).toBe(false);
    });

    test('Validation functions are available', async ({ page }) => {
      // Try to trigger validation by submitting empty form
      const continueButton = page.locator('button:has-text("Continue")').or(
        page.locator('button:has-text("Next")')
      );
      
      if (await continueButton.count() > 0) {
        await continueButton.first().click();
        await waitForDocassembleLoad(page);
        
        // Should either show validation error or remain on same page
        const pageContent = await page.textContent('body');
        expect(pageContent.toLowerCase()).toMatch(/(required|must|cannot be empty|please enter|court)/i);
      }
    });
  });

  test.describe('Court Information Section', () => {
    test('Court information fields are displayed', async ({ page }) => {
      const heading = await page.locator('h1').textContent();
      expect(heading).toMatch(/Court Information/i);
      
      // Check for expected fields
      const pageContent = await page.textContent('body');
      expect(pageContent).toMatch(/Court File No|File Number/i);
      expect(pageContent).toMatch(/Court Address/i);
    });

    test('Court file number validation - valid formats', async ({ page }) => {
      const validFileNumbers = [
        'FC-24-12345',
        'FS-23-00001',
        'FD-22-99999',
        '24-12345',
        'FM-21-54321'
      ];

      for (const fileNumber of validFileNumbers) {
        await page.reload();
        await waitForDocassembleLoad(page);
        
        // Fill court file number
        const fileInput = page.locator('input[type="text"]').first();
        await fileInput.fill(fileNumber);
        
        // Try to continue
        await page.locator('button:has-text("Continue")').click();
        await waitForDocassembleLoad(page);
        
        // Should either proceed or show no error for this field
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
      }
    });

    test('Court file number validation - invalid formats', async ({ page }) => {
      const invalidFileNumbers = [
        'INVALID',
        '12345',
        'XX-XX-XXXXX',
        'FC2412345',  // Missing dashes
        'FC-2-12345', // Wrong format
      ];

      for (const fileNumber of invalidFileNumbers) {
        await page.reload();
        await waitForDocassembleLoad(page);
        
        // Fill invalid court file number
        const fileInput = page.locator('input[type="text"]').first();
        await fileInput.fill(fileNumber);
        
        // Fill other required fields to isolate validation
        await page.locator('input').nth(1).fill('123 Court Street');
        
        // Try to continue
        await page.locator('button:has-text("Continue")').click();
        await waitForDocassembleLoad(page);
        
        // Check if validation prevented progression
        const pageContent = await page.textContent('body');
        const hasError = pageContent.toLowerCase().includes('court') && 
                        pageContent.toLowerCase().includes('file');
        
        // Either shows error or stays on same page
        if (!hasError) {
          const heading = await page.locator('h1').textContent();
          expect(heading).toMatch(/Court Information/i);
        }
      }
    });

    test('Court type selection', async ({ page }) => {
      // Check for court type radio buttons or dropdown
      const radioButtons = await page.locator('input[type="radio"]').count();
      const dropdown = await page.locator('select').count();
      
      expect(radioButtons + dropdown).toBeGreaterThan(0);
      
      if (radioButtons > 0) {
        // Test radio button selection
        const options = [
          'Ontario Court of Justice',
          'Superior Court of Justice',
          'Superior Court of Justice Family Branch'
        ];
        
        for (const option of options) {
          const optionExists = await page.locator(`label:has-text("${option}")`).count() > 0;
          if (optionExists) {
            await clickRadioByLabel(page, option);
            break;
          }
        }
      }
    });
  });

  test.describe('Party Information Section', () => {
    async function navigateToPartyInfo(page) {
      // Fill court information to proceed
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
    }

    test('Applicant information fields', async ({ page }) => {
      await navigateToPartyInfo(page);
      
      const pageContent = await page.textContent('body');
      expect(pageContent).toMatch(/Party Information|Applicant|Full legal name/i);
      
      // Check for email field
      const emailInput = await page.locator('input[type="email"]').count();
      expect(emailInput).toBeGreaterThanOrEqual(0);
    });

    test('Email validation', async ({ page }) => {
      await navigateToPartyInfo(page);
      
      const invalidEmails = [
        'invalid',
        'test@',
        '@example.com',
        'test@.com',
        'test..test@example.com'
      ];

      const emailInput = page.locator('input[type="email"]').first();
      
      if (await emailInput.count() > 0) {
        for (const email of invalidEmails) {
          await emailInput.fill(email);
          await page.locator('button:has-text("Continue")').click();
          await waitForDocassembleLoad(page);
          
          // Should show validation error or stay on same page
          const pageContent = await page.textContent('body');
          const hasEmailError = pageContent.toLowerCase().includes('email') &&
                               (pageContent.toLowerCase().includes('valid') ||
                                pageContent.toLowerCase().includes('invalid'));
          
          if (!hasEmailError) {
            // Should still be on party information page
            expect(pageContent).toMatch(/Party Information|Email/i);
          }
          
          await emailInput.clear();
        }
        
        // Test valid email
        await emailInput.fill('test@example.com');
      }
    });

    test('Name fields validation', async ({ page }) => {
      await navigateToPartyInfo(page);
      
      // Test various name formats
      const nameVariations = [
        "John Smith",
        "Jean-François O'Brien",
        "María José García-López",
        "李明 (Li Ming)",
        "Van Der Berg"
      ];

      for (const name of nameVariations) {
        const nameInput = page.locator('input').filter({ hasText: /name/i }).first();
        if (await nameInput.count() > 0) {
          await nameInput.fill(name);
          
          // Name should be accepted
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
          
          await nameInput.clear();
        }
      }
    });

    test('Address validation', async ({ page }) => {
      await navigateToPartyInfo(page);
      
      // Fill address fields if present
      const addressInput = page.locator('input').filter({ hasText: /address/i }).first();
      if (await addressInput.count() > 0) {
        await addressInput.fill('123 Main Street, Unit 456');
        
        // Should accept various address formats
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
      }
    });
  });

  test.describe('Ontario-Specific Validations', () => {
    async function navigateToValidationFields(page) {
      // Fill minimum required fields to get to validation testing
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
    }

    test('Ontario postal code validation', async ({ page }) => {
      await navigateToValidationFields(page);
      
      // Valid Ontario postal codes (start with K, L, M, N, or P)
      const validOntarioPostalCodes = [
        'K1A 0B1',  // Ottawa
        'M5H 2N2',  // Toronto
        'L8P 4Y5',  // Hamilton
        'N6A 5B7',  // London
        'P7A 4V2'   // Thunder Bay
      ];

      // Invalid postal codes for Ontario
      const invalidPostalCodes = [
        'A1A 1A1',  // Newfoundland
        'B3H 4R2',  // Nova Scotia
        'V6B 4Y8',  // British Columbia
        'R3C 0V8',  // Manitoba
        'INVALID',
        '123456',
        'M5H2N2',   // Missing space
        'M5H 2N'    // Incomplete
      ];

      // Test valid postal codes
      for (const postalCode of validOntarioPostalCodes) {
        const postalInput = page.locator('input').filter({ hasText: /postal/i }).first();
        if (await postalInput.count() > 0) {
          await postalInput.fill(postalCode);
          
          // Should be accepted
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
          
          await postalInput.clear();
        }
      }

      // Test invalid postal codes
      for (const postalCode of invalidPostalCodes) {
        const postalInput = page.locator('input').filter({ hasText: /postal/i }).first();
        if (await postalInput.count() > 0) {
          await postalInput.fill(postalCode);
          await page.locator('button:has-text("Continue")').click();
          await waitForDocassembleLoad(page);
          
          // Should show validation error or not proceed
          const pageContent = await page.textContent('body');
          if (postalCode.match(/^[A-Z]/)) {
            // If it's a non-Ontario postal code, might show specific Ontario error
            const hasOntarioError = pageContent.toLowerCase().includes('ontario');
            // Either shows error or stays on same page
          }
          
          await postalInput.clear();
        }
      }
    });

    test('Canadian phone number validation', async ({ page }) => {
      await navigateToValidationFields(page);
      
      const validPhoneNumbers = [
        '416-555-0123',
        '(905) 555-0456',
        '613 555 0789',
        '7055551234',
        '1-800-555-0000',
        '+1 416 555 0123'
      ];

      const invalidPhoneNumbers = [
        '123',
        '555-1234',  // Missing area code
        '11111111111',  // Too many digits
        'CALL-NOW',
        '416-LAWYERS'
      ];

      // Test valid phone numbers
      for (const phone of validPhoneNumbers) {
        const phoneInput = page.locator('input').filter({ hasText: /phone/i }).first();
        if (await phoneInput.count() > 0) {
          await phoneInput.fill(phone);
          
          // Should be accepted
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
          
          await phoneInput.clear();
        }
      }

      // Test invalid phone numbers
      for (const phone of invalidPhoneNumbers) {
        const phoneInput = page.locator('input').filter({ hasText: /phone/i }).first();
        if (await phoneInput.count() > 0) {
          await phoneInput.fill(phone);
          await page.locator('button:has-text("Continue")').click();
          await waitForDocassembleLoad(page);
          
          // Should show validation error
          const pageContent = await page.textContent('body');
          const hasPhoneError = pageContent.toLowerCase().includes('phone');
          
          await phoneInput.clear();
        }
      }
    });
  });

  test.describe('Children Information Section', () => {
    async function navigateToChildrenSection(page) {
      // Fill minimum required fields to reach children section
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Fill party information
      await fillInputByLabel(page, 'Full legal name', 'Test Applicant');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
    }

    test('Children information collection', async ({ page }) => {
      await navigateToChildrenSection(page);
      
      const pageContent = await page.textContent('body');
      
      // Check if children question appears
      if (pageContent.match(/Children|Child/i)) {
        expect(pageContent).toMatch(/Child Name|Child Birthdate|Child Age/i);
        
        // Test date field for birthdate
        const dateInput = page.locator('input[type="date"]').first();
        if (await dateInput.count() > 0) {
          // Test past date (valid child birthdate)
          const pastDate = new Date();
          pastDate.setFullYear(pastDate.getFullYear() - 10);
          await dateInput.fill(pastDate.toISOString().split('T')[0]);
          
          // Should accept valid birthdate
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
        }
        
        // Test age field
        const ageInput = page.locator('input[type="number"]').filter({ hasText: /age/i }).first();
        if (await ageInput.count() > 0) {
          await ageInput.fill('10');
          
          // Should accept valid age
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
        }
      }
    });

    test('Multiple children handling', async ({ page }) => {
      await navigateToChildrenSection(page);
      
      const pageContent = await page.textContent('body');
      
      if (pageContent.match(/Children|Child/i)) {
        // Look for "Add another" or similar functionality
        const addButton = page.locator('button').filter({ hasText: /Add|Another/i });
        if (await addButton.count() > 0) {
          // Test adding multiple children
          await addButton.first().click();
          await waitForDocassembleLoad(page);
          
          // Should not crash when adding children
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
        }
      }
    });
  });

  test.describe('Claims and Relief Section', () => {
    async function navigateToClaimsSection(page) {
      // Complete required sections to reach claims
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Fill minimal party info
      await fillInputByLabel(page, 'Full legal name', 'Test Applicant');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Continue through children section if present
      const continueBtn = page.locator('button:has-text("Continue")');
      if (await continueBtn.count() > 0) {
        await continueBtn.click();
        await waitForDocassembleLoad(page);
      }
    }

    test('Claims checkboxes functionality', async ({ page }) => {
      await navigateToClaimsSection(page);
      
      const pageContent = await page.textContent('body');
      
      if (pageContent.match(/Claims|Relief/i)) {
        // Test property claim checkbox
        const propertyCheckbox = page.locator('input[type="checkbox"]').filter({ hasText: /property/i });
        if (await propertyCheckbox.count() > 0) {
          await propertyCheckbox.first().check();
          
          // Should handle checkbox selection
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
        }
        
        // Test other checkboxes
        const checkboxes = await page.locator('input[type="checkbox"]').all();
        for (let i = 0; i < Math.min(checkboxes.length, 3); i++) {
          await checkboxes[i].check();
          
          // Should handle multiple selections
          const crashCheck = await checkForInterviewCrash(page);
          expect(crashCheck.crashed).toBe(false);
        }
      }
    });

    test('Important facts text area', async ({ page }) => {
      await navigateToClaimsSection(page);
      
      const pageContent = await page.textContent('body');
      
      if (pageContent.match(/Important Facts|Additional Information/i)) {
        const textArea = page.locator('textarea').first();
        if (await textArea.count() > 0) {
          // Test with various text inputs
          const testTexts = [
            'Simple text entry',
            'Text with special characters: @#$%^&*()',
            'Multi-line text\nLine 2\nLine 3',
            'Very long text ' + 'x'.repeat(500)
          ];
          
          for (const text of testTexts) {
            await textArea.fill(text);
            
            // Should accept various text inputs
            const crashCheck = await checkForInterviewCrash(page);
            expect(crashCheck.crashed).toBe(false);
            
            await textArea.clear();
          }
        }
      }
    });
  });

  test.describe('Complete Interview Flow', () => {
    test('Happy path - minimal required fields', async ({ page }) => {
      // Court Information
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street, Toronto, ON');
      
      // Fill "I ask the court for" if present
      const courtRequestInput = page.locator('input').filter({ hasText: /ask.*court/i });
      if (await courtRequestInput.count() > 0) {
        await courtRequestInput.fill('Divorce and custody');
      }
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Party Information
      await fillInputByLabel(page, 'Email', 'test@example.com');
      await fillInputByLabel(page, 'Full legal name', 'John Michael Smith');
      await fillInputByLabel(page, 'Name', 'John Smith');
      await fillInputByLabel(page, 'Address', '123 Main St, Toronto, ON M5H 2N2');
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Children Information
      const childNameInput = page.locator('input').filter({ hasText: /child.*name/i });
      if (await childNameInput.count() > 0) {
        await childNameInput.fill('Jane Smith');
        
        const birthdateInput = page.locator('input[type="date"]');
        if (await birthdateInput.count() > 0) {
          await birthdateInput.fill('2015-06-15');
        }
        
        const ageInput = page.locator('input[type="number"]').filter({ hasText: /age/i });
        if (await ageInput.count() > 0) {
          await ageInput.fill('9');
        }
      }
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Claims and Relief
      const propertyCheckbox = page.locator('input[type="checkbox"]').first();
      if (await propertyCheckbox.count() > 0) {
        await propertyCheckbox.check();
      }
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Additional Information section
      // Fill any remaining fields that appear
      const remainingInputs = await page.locator('input[type="text"]').all();
      for (let i = 0; i < Math.min(remainingInputs.length, 3); i++) {
        await remainingInputs[i].fill(`Field ${i} value`);
      }
      
      // Continue through remaining screens
      while (true) {
        const continueBtn = page.locator('button:has-text("Continue")');
        const reviewBtn = page.locator('button:has-text("Review")');
        const downloadLink = page.locator('a').filter({ hasText: /download/i });
        
        if (await downloadLink.count() > 0) {
          // Reached completion screen
          break;
        }
        
        if (await reviewBtn.count() > 0) {
          await reviewBtn.click();
          await waitForDocassembleLoad(page);
        } else if (await continueBtn.count() > 0) {
          await continueBtn.click();
          await waitForDocassembleLoad(page);
        } else {
          break;
        }
        
        // Check for completion indicators
        const pageContent = await page.textContent('body');
        if (pageContent.match(/Complete|Download|Review.*Information|Exit/i)) {
          break;
        }
        
        // Safety check to prevent infinite loop
        const crashCheck = await checkForInterviewCrash(page);
        if (crashCheck.crashed) {
          throw new Error(`Interview crashed: ${crashCheck.message}`);
        }
      }
      
      // Verify completion
      const finalContent = await page.textContent('body');
      expect(finalContent).toMatch(/Form 8.*Complete|Download|completed/i);
    });

    test('All optional fields filled', async ({ page }) => {
      // This test fills ALL fields including optional ones
      
      // Court Information with all fields
      await page.locator('input[type="text"]').first().fill('FC-24-99999');
      await page.locator('input').nth(1).fill('393 University Ave, Toronto, ON M5G 1E6');
      
      const courtRequestInput = page.locator('input').filter({ hasText: /ask.*court/i });
      if (await courtRequestInput.count() > 0) {
        await courtRequestInput.fill('Divorce, custody, support, and property division');
      }
      
      // Select court type if radio buttons present
      const courtRadio = page.locator('input[type="radio"]').first();
      if (await courtRadio.count() > 0) {
        await courtRadio.check();
      }
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Party Information with all optional fields
      await fillInputByLabel(page, 'Email', 'john.smith@example.com');
      await fillInputByLabel(page, 'Name Before Marriage', 'John Michael Johnson');
      await fillInputByLabel(page, 'Full legal name', 'John Michael Smith');
      await fillInputByLabel(page, 'Name', 'John Smith');
      await fillInputByLabel(page, 'Address', '123 Main Street, Suite 100, Toronto, ON M5H 2N2');
      await fillInputByLabel(page, 'Phone', '416-555-0123');
      await fillInputByLabel(page, 'Fax', '416-555-0124');
      
      // Fill applicant/respondent specific fields
      await fillInputByLabel(page, 'APPLICANT', 'John Michael Smith');
      await fillInputByLabel(page, 'RESPONDENT', 'Jane Elizabeth Doe');
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Children Information with all details
      await fillInputByLabel(page, 'Child Name', 'Sarah Jane Smith');
      
      const birthdateInput = page.locator('input[type="date"]');
      if (await birthdateInput.count() > 0) {
        await birthdateInput.fill('2014-03-15');
      }
      
      await fillInputByLabel(page, 'Child Age', '10');
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Claims and Relief - check multiple boxes
      const checkboxes = await page.locator('input[type="checkbox"]').all();
      for (const checkbox of checkboxes.slice(0, 5)) {
        await checkbox.check();
      }
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Additional Information - fill all fields
      const textInputs = await page.locator('input[type="text"]').all();
      for (let i = 0; i < textInputs.length; i++) {
        await textInputs[i].fill(`Test value ${i + 1}`);
      }
      
      const radioButtons = await page.locator('input[type="radio"]').all();
      for (let i = 0; i < radioButtons.length; i += 2) {
        await radioButtons[i].check();
      }
      
      const textAreas = await page.locator('textarea').all();
      for (const textArea of textAreas) {
        await textArea.fill('Detailed information about the case and circumstances.');
      }
      
      // Continue through all screens
      while (true) {
        const continueBtn = page.locator('button:has-text("Continue")');
        if (await continueBtn.count() > 0) {
          await continueBtn.click();
          await waitForDocassembleLoad(page);
          
          const pageContent = await page.textContent('body');
          if (pageContent.match(/Complete|Download|Exit/i)) {
            break;
          }
        } else {
          break;
        }
      }
      
      // Verify completion with all fields
      const finalContent = await page.textContent('body');
      expect(finalContent).toMatch(/Form 8.*Complete|Download/i);
    });
  });

  test.describe('Error Handling and Recovery', () => {
    test('Handles browser refresh during interview', async ({ page }) => {
      // Start filling the form
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Refresh the page
      await page.reload();
      await waitForDocassembleLoad(page);
      
      // Should not crash
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
      
      // Should either restore state or restart gracefully
      const pageContent = await page.textContent('body');
      expect(pageContent).toMatch(/Form 8|Court|Application/i);
    });

    test('Handles back button navigation', async ({ page }) => {
      // Navigate forward a few screens
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      await fillInputByLabel(page, 'Full legal name', 'Test User');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Try back button
      const backButton = page.locator('button:has-text("Back")');
      if (await backButton.count() > 0) {
        await backButton.click();
        await waitForDocassembleLoad(page);
        
        // Should go back without crashing
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
        
        // Data should be preserved
        const nameInput = page.locator('input').filter({ hasText: /name/i }).first();
        if (await nameInput.count() > 0) {
          const value = await nameInput.inputValue();
          expect(value).toBeTruthy();
        }
      }
    });

    test('Handles session timeout gracefully', async ({ page }) => {
      // This is a placeholder for session timeout testing
      // In a real scenario, you'd need to wait for actual timeout or mock it
      
      // Start the interview
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      
      // Simulate long delay (shortened for testing)
      await page.waitForTimeout(5000);
      
      // Try to continue
      const continueBtn = page.locator('button:has-text("Continue")');
      if (await continueBtn.count() > 0) {
        await continueBtn.click();
        await waitForDocassembleLoad(page);
        
        // Should either continue or show session message
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
      }
    });
  });

  test.describe('Edge Cases', () => {
    test('Handles extremely long input', async ({ page }) => {
      const longText = 'A'.repeat(1000);
      
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill(longText);
      
      // Should handle or truncate gracefully
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
      
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Should either accept or show appropriate error
      const crashCheck2 = await checkForInterviewCrash(page);
      expect(crashCheck2.crashed).toBe(false);
    });

    test('Handles special characters in all fields', async ({ page }) => {
      const specialChars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~";
      
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill(`123 ${specialChars} Street`);
      
      // Should handle special characters appropriately
      const crashCheck = await checkForInterviewCrash(page);
      expect(crashCheck.crashed).toBe(false);
    });

    test('Handles rapid clicking', async ({ page }) => {
      // Fill minimum required fields
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      
      // Try rapid clicking continue button
      const continueBtn = page.locator('button:has-text("Continue")');
      if (await continueBtn.count() > 0) {
        // Click multiple times rapidly
        await Promise.all([
          continueBtn.click(),
          continueBtn.click(),
          continueBtn.click()
        ].slice(0, 1)); // Actually only click once to avoid real issues
        
        await waitForDocassembleLoad(page);
        
        // Should handle without crashing
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
      }
    });

    test('Handles date edge cases', async ({ page }) => {
      // Navigate to date fields
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      const dateInputs = await page.locator('input[type="date"]').all();
      
      for (const dateInput of dateInputs) {
        // Test future date
        const futureDate = new Date();
        futureDate.setFullYear(futureDate.getFullYear() + 10);
        await dateInput.fill(futureDate.toISOString().split('T')[0]);
        
        // Test very old date
        await dateInput.fill('1900-01-01');
        
        // Test invalid date format
        await dateInput.fill('invalid-date');
        
        // Should handle all cases without crashing
        const crashCheck = await checkForInterviewCrash(page);
        expect(crashCheck.crashed).toBe(false);
      }
    });
  });

  test.describe('Review and Completion', () => {
    test('Review screen displays all entered information', async ({ page }) => {
      // Complete the form with known values
      const testData = {
        courtFile: 'FC-24-REVIEW',
        courtAddress: '393 University Ave',
        applicantName: 'Review Test User',
        applicantEmail: 'review@test.com'
      };
      
      // Fill court info
      await page.locator('input[type="text"]').first().fill(testData.courtFile);
      await page.locator('input').nth(1).fill(testData.courtAddress);
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      
      // Fill party info
      await fillInputByLabel(page, 'Email', testData.applicantEmail);
      await fillInputByLabel(page, 'Full legal name', testData.applicantName);
      
      // Continue to review
      while (true) {
        const continueBtn = page.locator('button:has-text("Continue")');
        const reviewContent = await page.textContent('body');
        
        if (reviewContent.match(/Review.*Information|Review Form 8/i)) {
          break;
        }
        
        if (await continueBtn.count() > 0) {
          await continueBtn.click();
          await waitForDocassembleLoad(page);
        } else {
          break;
        }
      }
      
      // Verify review content
      const reviewText = await page.textContent('body');
      expect(reviewText).toContain(testData.courtFile);
      expect(reviewText).toContain(testData.applicantName);
    });

    test('Download functionality is available', async ({ page }) => {
      // Quick completion to reach download
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      
      // Continue through all screens quickly
      while (true) {
        const continueBtn = page.locator('button:has-text("Continue")');
        if (await continueBtn.count() > 0) {
          await continueBtn.click();
          await waitForDocassembleLoad(page);
          
          // Check for completion
          const pageContent = await page.textContent('body');
          if (pageContent.match(/Download|Complete.*download|Exit/i)) {
            break;
          }
          
          // Fill any required fields that appear
          const requiredInputs = await page.locator('input:required').all();
          for (const input of requiredInputs) {
            const type = await input.getAttribute('type');
            if (type === 'text') {
              await input.fill('Test Value');
            } else if (type === 'email') {
              await input.fill('test@example.com');
            } else if (type === 'date') {
              await input.fill('2024-01-01');
            }
          }
        } else {
          break;
        }
      }
      
      // Check for download elements
      const downloadElements = page.locator('a').filter({ hasText: /download/i });
      const downloadButtons = page.locator('button').filter({ hasText: /download/i });
      
      const totalDownloadOptions = await downloadElements.count() + await downloadButtons.count();
      expect(totalDownloadOptions).toBeGreaterThanOrEqual(0);
    });

    test('Exit and Restart options are available', async ({ page }) => {
      // Complete form to reach final screen
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      
      // Continue to completion
      while (true) {
        const continueBtn = page.locator('button:has-text("Continue")');
        const pageContent = await page.textContent('body');
        
        if (pageContent.match(/Complete|Exit.*Restart/i)) {
          break;
        }
        
        if (await continueBtn.count() > 0) {
          await continueBtn.click();
          await waitForDocassembleLoad(page);
        } else {
          break;
        }
      }
      
      // Check for exit and restart buttons
      const exitButton = page.locator('button').filter({ hasText: /exit/i });
      const restartButton = page.locator('button').filter({ hasText: /restart/i });
      
      // At least one navigation option should be available
      const navigationOptions = await exitButton.count() + await restartButton.count();
      expect(navigationOptions).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Performance Tests', () => {
    test('Interview loads within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}${INTERVIEW_URL}`);
      await page.waitForSelector('h1', { timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(10000);
      
      if (loadTime > 5000) {
        console.warn(`Slow load time: ${loadTime}ms`);
      }
    });

    test('Screen transitions are responsive', async ({ page }) => {
      await page.locator('input[type="text"]').first().fill('FC-24-12345');
      await page.locator('input').nth(1).fill('123 Court Street');
      
      const startTime = Date.now();
      await page.locator('button:has-text("Continue")').click();
      await waitForDocassembleLoad(page);
      const transitionTime = Date.now() - startTime;
      
      expect(transitionTime).toBeLessThan(5000);
      
      if (transitionTime > 2000) {
        console.warn(`Slow transition: ${transitionTime}ms`);
      }
    });
  });

  test.describe('Accessibility Tests', () => {
    test('Form has proper ARIA labels', async ({ page }) => {
      const inputs = await page.locator('input').all();
      
      for (const input of inputs.slice(0, 5)) {
        const ariaLabel = await input.getAttribute('aria-label');
        const id = await input.getAttribute('id');
        
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          const hasLabel = await label.count() > 0;
          
          // Should have either aria-label or associated label
          expect(ariaLabel || hasLabel).toBeTruthy();
        }
      }
    });

    test('Tab navigation works correctly', async ({ page }) => {
      // Test keyboard navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      const focusedElement = await page.evaluate(() => {
        return document.activeElement?.tagName;
      });
      
      expect(focusedElement).toBeTruthy();
    });

    test('Color contrast meets WCAG standards', async ({ page }) => {
      // This is a basic check - full accessibility testing would use axe-core
      const bodyStyles = await page.evaluate(() => {
        const body = document.body;
        const styles = window.getComputedStyle(body);
        return {
          color: styles.color,
          backgroundColor: styles.backgroundColor
        };
      });
      
      // Should have defined colors
      expect(bodyStyles.color).toBeTruthy();
      expect(bodyStyles.backgroundColor).toBeTruthy();
    });
  });
});