const { test, expect } = require('@playwright/test');
const { WizardPage } = require('../pages/WizardPage');

/**
 * Field Validation and Edge Cases Test Suite
 * Tests all field validation rules, boundary conditions, and edge cases
 */
test.describe('Field Validation and Edge Cases', () => {
  let wizardPage;

  test.beforeEach(async ({ page }) => {
    wizardPage = new WizardPage(page);
    await wizardPage.goto();
  });

  test.describe('Required Field Validation', () => {
    test('should validate empty required fields on party information', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      // Select divorce only to get to party info quickly
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Now we should be at party information
      // Try to continue without filling any fields
      await wizardPage.clickContinue();
      
      // Check for validation errors
      const errors = await wizardPage.page.locator('.da-error, .text-danger, .alert-danger');
      const errorCount = await errors.count();
      expect(errorCount).toBeGreaterThan(0);
    });

    test('should validate partial field completion', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Fill only first name
      await wizardPage.fillPartyInformation('applicant', {
        firstName: 'John'
        // Missing lastName, address, etc.
      });
      
      await wizardPage.clickContinue();
      
      // Should still show validation errors
      const errors = await wizardPage.page.locator('.da-error, .text-danger, .alert-danger');
      const errorCount = await errors.count();
      expect(errorCount).toBeGreaterThan(0);
    });
  });

  test.describe('Email Validation', () => {
    test('should reject invalid email formats', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Try various invalid email formats
      const invalidEmails = [
        'notanemail',
        '@example.com',
        'user@',
        'user@@example.com',
        'user@example',
        'user name@example.com',
        'user@exam ple.com'
      ];
      
      for (const invalidEmail of invalidEmails) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: 'John',
          lastName: 'Smith',
          email: invalidEmail,
          phone: '4165551234',
          address: '123 Main St',
          city: 'Toronto',
          province: 'ON',
          postalCode: 'M5H 2N2'
        });
        
        await wizardPage.clickContinue();
        
        // Should show validation error for invalid email
        const errors = await wizardPage.page.locator('.da-error, .text-danger, .alert-danger');
        const errorCount = await errors.count();
        expect(errorCount, `Should reject email: ${invalidEmail}`).toBeGreaterThan(0);
      }
    });

    test('should accept valid email formats', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Try valid email formats
      const validEmails = [
        'user@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_name@example-domain.com',
        '123@example.com'
      ];
      
      for (const validEmail of validEmails) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: 'John',
          lastName: 'Smith',
          email: validEmail,
          phone: '4165551234',
          address: '123 Main St',
          city: 'Toronto',
          province: 'ON',
          postalCode: 'M5H 2N2'
        });
        
        await wizardPage.clickContinue();
        
        // Should proceed without email validation errors
        // Check we moved to next screen
        const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
        expect(questionText).not.toContain('Your Information');
      }
    });
  });

  test.describe('Phone Number Validation', () => {
    test('should validate phone number formats', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Test various phone formats
      const phoneNumbers = [
        '4165551234',      // 10 digits no formatting
        '416-555-1234',    // With dashes
        '(416) 555-1234',  // With parentheses
        '416.555.1234',    // With dots
        '416 555 1234',    // With spaces
        '+14165551234',    // International format
        '1-416-555-1234'   // With country code
      ];
      
      for (const phone of phoneNumbers) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: 'John',
          lastName: 'Smith',
          email: 'john@example.com',
          phone: phone,
          address: '123 Main St',
          city: 'Toronto',
          province: 'ON',
          postalCode: 'M5H 2N2'
        });
        
        await wizardPage.clickContinue();
        
        // Should accept various phone formats
        const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
        expect(questionText).not.toContain('Your Information');
      }
    });
  });

  test.describe('Postal Code Validation', () => {
    test('should validate Canadian postal code format', async () => {
      // Navigate to party information
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Test valid Canadian postal codes
      const validPostalCodes = [
        'M5H 2N2',
        'M5H2N2',
        'K1A 0B1',
        'V6B 4Y8',
        'T2P 1J9'
      ];
      
      for (const postalCode of validPostalCodes) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: 'John',
          lastName: 'Smith',
          email: 'john@example.com',
          phone: '4165551234',
          address: '123 Main St',
          city: 'Toronto',
          province: 'ON',
          postalCode: postalCode
        });
        
        await wizardPage.clickContinue();
        
        // Should accept valid postal codes
        const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
        expect(questionText).not.toContain('Your Information');
      }
    });
  });

  test.describe('Date Field Validation', () => {
    test('should validate date formats and ranges', async () => {
      // Navigate to a screen with date fields
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Test various date scenarios
      const today = new Date();
      const futureDate = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate());
      const pastDate = new Date(1950, 0, 1);
      const invalidDate = new Date(1800, 0, 1); // Too far in the past
      
      // Birth dates should be in the past
      await wizardPage.fillPartyInformation('applicant', {
        firstName: 'John',
        lastName: 'Smith',
        email: 'john@example.com',
        phone: '4165551234',
        address: '123 Main St',
        city: 'Toronto',
        province: 'ON',
        postalCode: 'M5H 2N2',
        birthDate: pastDate.toISOString().split('T')[0]
      });
      
      await wizardPage.clickContinue();
      
      // Should accept valid past date
      const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
      expect(questionText).not.toContain('Your Information');
    });
  });

  test.describe('Financial Value Validation', () => {
    test('should validate financial value inputs', async () => {
      // Navigate to financial situation
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: true,
        property: true,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      // Test various financial values
      const testValues = [
        { value: '0', valid: true },
        { value: '50000', valid: true },
        { value: '1000000', valid: true },
        { value: '50000.50', valid: true },
        { value: '-1000', valid: false },
        { value: 'abc', valid: false },
        { value: '1,000,000', valid: true }, // With commas
        { value: '$50000', valid: true }      // With dollar sign
      ];
      
      for (const testCase of testValues) {
        await wizardPage.handleFinancialSituation({
          property_value: testCase.value,
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });
        
        if (testCase.valid) {
          // Should proceed to next screen
          await wizardPage.waitForQuestion('Your Personalized Forms Package');
        } else {
          // Should show validation error
          const errors = await wizardPage.page.locator('.da-error, .text-danger, .alert-danger');
          const errorCount = await errors.count();
          expect(errorCount).toBeGreaterThan(0);
        }
      }
    });

    test('should handle boundary values for financial thresholds', async () => {
      // Navigate to financial situation
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: true,
        property: true,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      // Test boundary values
      const boundaryValues = [
        49999,  // Just below $50,000 threshold
        50000,  // Exactly at threshold
        50001,  // Just above threshold
        99999,  // Just below $100,000
        100000, // At $100,000
        100001  // Above $100,000
      ];
      
      for (const value of boundaryValues) {
        await wizardPage.handleFinancialSituation({
          property_value: value,
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });
        
        await wizardPage.handleRecommendations();
        
        // Check which form is recommended based on value
        const forms = await wizardPage.getRecommendedForms();
        
        if (value < 50000) {
          // Should recommend Form 13
          expect(forms.some(f => f.includes('Form 13') && !f.includes('13.1'))).toBe(true);
        } else {
          // Should recommend Form 13.1
          expect(forms.some(f => f.includes('Form 13.1'))).toBe(true);
        }
        
        // Navigate back for next test
        await wizardPage.page.goBack();
      }
    });
  });

  test.describe('Checkbox Selection Edge Cases', () => {
    test('should handle no orders selected', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      // Don't select any orders
      await wizardPage.handleOrdersSought({
        divorce: false,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      // Should either show validation or proceed with minimal forms
      const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
      
      // Check if validation message appears or if it continues
      if (questionText.includes('orders')) {
        // Still on orders page - validation occurred
        const errors = await wizardPage.page.locator('.da-error, .text-danger');
        expect(await errors.count()).toBeGreaterThan(0);
      } else {
        // Proceeded - check that minimal forms are recommended
        await wizardPage.handleRecommendations();
        const forms = await wizardPage.getRecommendedForms();
        expect(forms.length).toBeGreaterThan(0);
      }
    });

    test('should handle all orders selected', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      // Select all orders
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: true,
        exclusive_possession: true,
        restraining_order: true,
        enforcement: true,
        other: true
      });
      
      // Should proceed to financial questions
      await wizardPage.handleFinancialSituation({
        property_value: 100000,
        support_involved: true,
        business_owner: true,
        pension_involved: true
      });
      
      await wizardPage.handleRecommendations();
      
      // Should recommend comprehensive form package
      const forms = await wizardPage.getRecommendedForms();
      expect(forms.length).toBeGreaterThan(5); // Multiple forms needed
      
      // Should include divorce form
      expect(forms.some(f => f.includes('Form 8A'))).toBe(true);
      // Should include financial forms
      expect(forms.some(f => f.includes('Form 13'))).toBe(true);
    });
  });

  test.describe('Special Characters and Unicode', () => {
    test('should handle special characters in names', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Test names with special characters
      const specialNames = [
        { first: "Jean-Pierre", last: "O'Connor" },
        { first: "María", last: "González" },
        { first: "François", last: "Côté" },
        { first: "李", last: "王" }, // Chinese characters
        { first: "محمد", last: "أحمد" } // Arabic characters
      ];
      
      for (const name of specialNames) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: name.first,
          lastName: name.last,
          email: 'test@example.com',
          phone: '4165551234',
          address: '123 Main St',
          city: 'Toronto',
          province: 'ON',
          postalCode: 'M5H 2N2'
        });
        
        await wizardPage.clickContinue();
        
        // Should accept special characters
        const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
        expect(questionText).not.toContain('Your Information');
      }
    });

    test('should handle special characters in addresses', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      await wizardPage.handleChildrenInvolved(false);
      
      // Test addresses with special characters
      const specialAddresses = [
        "123 Rue Saint-Jean, Apt #5",
        "456 O'Connor Street",
        "789 King St. West, Unit 10-B",
        "1234 Avenue des Érables",
        "5678 Queen's Park Circle"
      ];
      
      for (const address of specialAddresses) {
        await wizardPage.fillPartyInformation('applicant', {
          firstName: 'John',
          lastName: 'Smith',
          email: 'test@example.com',
          phone: '4165551234',
          address: address,
          city: 'Toronto',
          province: 'ON',
          postalCode: 'M5H 2N2'
        });
        
        await wizardPage.clickContinue();
        
        // Should accept special characters in addresses
        const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
        expect(questionText).not.toContain('Your Information');
      }
    });
  });

  test.describe('Browser Navigation Edge Cases', () => {
    test('should handle browser back button gracefully', async () => {
      // Navigate through several screens
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      // Use browser back button
      await wizardPage.page.goBack();
      await wizardPage.page.waitForLoadState('networkidle');
      
      // Should be back at relationship status
      const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
      expect(questionText).toContain('relationship status');
      
      // Continue forward again
      await wizardPage.handleRelationshipStatus('married');
      
      // Should continue normally
      await wizardPage.waitForQuestionContaining(['orders', 'seeking']);
    });

    test('should handle browser refresh', async () => {
      // Navigate to middle of interview
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      
      // Refresh the page
      await wizardPage.page.reload();
      await wizardPage.page.waitForLoadState('networkidle');
      
      // Should maintain session and show current question
      const questionText = await wizardPage.page.locator('#daMainQuestion').textContent();
      expect(questionText).toBeTruthy();
      
      // Should not show error
      await wizardPage.checkForErrors();
    });
  });

  test.describe('Conditional Logic Edge Cases', () => {
    test('should handle complex conditional paths', async () => {
      // Test: Married + Divorce + Children + Property + Support
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: true,
        child_support: true,
        spousal_support: true,
        property: true,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      // Should skip divorce complexity question and go to financial
      await wizardPage.handleFinancialSituation({
        property_value: 150000,
        support_involved: true,
        business_owner: true,
        pension_involved: true
      });
      
      await wizardPage.handleRecommendations();
      
      // Verify correct forms for complex case
      const forms = await wizardPage.getRecommendedForms();
      expect(forms.some(f => f.includes('Form 8A'))).toBe(true); // Divorce
      expect(forms.some(f => f.includes('Form 13.1'))).toBe(true); // High-value property
      expect(forms.some(f => f.includes('Form 35.1'))).toBe(true); // Children
    });

    test('should handle changing answers via back button', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      await wizardPage.handleOrdersSought({
        divorce: true,
        custody: false,
        child_support: false,
        spousal_support: false,
        property: false,
        exclusive_possession: false,
        restraining_order: false,
        enforcement: false,
        other: false
      });
      
      await wizardPage.handleDivorceComplexity('uncontested');
      
      // Go back and change to contested
      await wizardPage.page.goBack();
      await wizardPage.page.waitForLoadState('networkidle');
      
      await wizardPage.handleDivorceComplexity('contested');
      
      // Should now go to financial questions instead of children question
      await wizardPage.waitForQuestion('What is your financial situation?');
    });
  });

  test.describe('Session and Timeout Handling', () => {
    test('should handle session continuation after delay', async () => {
      await wizardPage.handleIntroduction();
      await wizardPage.handleEmergencyQuestion(false);
      
      // Wait for 2 seconds (simulating user delay)
      await wizardPage.page.waitForTimeout(2000);
      
      // Continue with interview
      await wizardPage.handleMipQuestion('completed');
      await wizardPage.handleRelationshipStatus('married');
      
      // Should continue normally
      await wizardPage.waitForQuestionContaining(['orders', 'seeking']);
    });
  });

  test.describe('Accessibility and Keyboard Navigation', () => {
    test('should be navigable via keyboard', async () => {
      await wizardPage.handleIntroduction();
      
      // Use Tab key to navigate to emergency question buttons
      await wizardPage.page.keyboard.press('Tab');
      await wizardPage.page.keyboard.press('Tab');
      
      // Press Enter to select "No"
      await wizardPage.page.keyboard.press('Enter');
      await wizardPage.page.waitForLoadState('networkidle');
      
      // Should have proceeded to MIP question
      await wizardPage.waitForQuestion('Mandatory Information Program');
    });
  });
});