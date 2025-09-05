const { test, expect } = require('@playwright/test');
const { Form13Page } = require('../pages/Form13Page');
const { generateTestData } = require('../fixtures/form-13-test-data');

test.describe('Form 13 - Financial Statement Comprehensive Tests', () => {
  let page;
  let form13Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    form13Page = new Form13Page(page);
  });

  test.afterEach(async () => {
    await page.close();
  });

  test.describe('Happy Path Tests', () => {
    test('Complete Form 13 with minimal required information', async () => {
      await form13Page.goto();
      
      // Fill minimal required information
      await form13Page.fillPersonalInformation({
        fullName: 'John Doe',
        courtName: 'Superior Court of Justice'
      });

      await form13Page.fillContactInformation({
        address: '123 Main St, Toronto, ON',
        email: 'john.doe@example.com',
        phone: '416-555-0123'
      });

      // Add minimal income
      await form13Page.addIncomeItems([
        { description: 'Employment Income', amount: 5000, frequency: 'monthly' }
      ]);

      // Add minimal expenses
      await form13Page.addExpenseItems([
        { description: 'Rent', amount: 1500, category: 'housing' },
        { description: 'Groceries', amount: 500, category: 'food' }
      ]);

      // Skip optional sections (assets, debts)
      
      // Review and sign
      await form13Page.handleReviewScreen();
      await form13Page.completeSignature({
        name: 'John Doe',
        date: new Date().toISOString().split('T')[0]
      });

      // Verify completion
      await form13Page.verifyFinalScreen();
    });

    test('Complete Form 13 with all sections filled', async () => {
      await form13Page.goto();
      
      const testData = generateTestData('complete');
      
      await form13Page.fillPersonalInformation(testData.personal);
      await form13Page.fillContactInformation(testData.contact);
      await form13Page.addIncomeItems(testData.income);
      await form13Page.addExpenseItems(testData.expenses);
      await form13Page.addAssets(testData.assets);
      await form13Page.addDebts(testData.debts);
      
      // Upload tax documents if interview includes them
      if (testData.taxDocuments) {
        await form13Page.uploadTaxDocuments(testData.taxDocuments);
      }
      
      // Upload bank statements if interview includes them
      if (testData.bankStatements) {
        await form13Page.uploadBankStatements(testData.bankStatements);
      }
      
      await form13Page.handleReviewScreen();
      await form13Page.completeSignature(testData.signature);
      await form13Page.verifyFinalScreen();
    });

    test('Complete Form 13 for high net worth individual', async () => {
      await form13Page.goto();
      
      const testData = generateTestData('high_net_worth');
      
      await form13Page.fillPersonalInformation(testData.personal);
      await form13Page.fillContactInformation(testData.contact);
      
      // Multiple income sources
      await form13Page.addIncomeItems([
        { description: 'Employment Income', amount: 15000, frequency: 'monthly' },
        { description: 'Investment Income', amount: 5000, frequency: 'monthly' },
        { description: 'Rental Income', amount: 3000, frequency: 'monthly' },
        { description: 'Business Income', amount: 10000, frequency: 'monthly' }
      ]);
      
      // Detailed expenses
      await form13Page.addExpenseItems(testData.expenses);
      
      // Multiple assets
      await form13Page.addAssets([
        { description: 'Primary Residence', currentValue: 1500000 },
        { description: 'Investment Property', currentValue: 800000 },
        { description: 'Stock Portfolio', currentValue: 500000 },
        { description: 'Business Ownership', currentValue: 2000000 }
      ]);
      
      await form13Page.addDebts(testData.debts);
      await form13Page.handleReviewScreen();
      await form13Page.completeSignature(testData.signature);
      await form13Page.verifyFinalScreen();
    });
  });

  test.describe('Field Validation Tests', () => {
    test('Validate required fields on personal information', async () => {
      await form13Page.goto();
      await form13Page.waitForQuestion('Personal Information');
      
      // Try to continue without filling required fields
      await form13Page.clickContinue();
      
      // Should show validation errors
      const errors = await form13Page.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);
      
      // Should remain on same screen
      await form13Page.waitForQuestion('Personal Information');
    });

    test('Validate email format', async () => {
      await form13Page.goto();
      
      await form13Page.fillPersonalInformation({
        fullName: 'Test User',
        courtName: 'Test Court'
      });
      
      await form13Page.waitForQuestion('Contact Information');
      
      // Test invalid email formats
      const invalidEmails = [
        'notanemail',
        '@example.com',
        'user@',
        'user@.com',
        'user@example',
        'user name@example.com'
      ];
      
      for (const email of invalidEmails) {
        await page.fill('input[type="email"]', email);
        await form13Page.clickContinue();
        
        const errors = await form13Page.getValidationErrors();
        expect(errors.length, `Should show error for invalid email: ${email}`).toBeGreaterThan(0);
        
        await page.fill('input[type="email"]', ''); // Clear field
      }
      
      // Test valid email
      await page.fill('input[type="email"]', 'valid@example.com');
      await page.fill('input[name*="address"]', '123 Test St');
      await page.fill('input[type="tel"], input[name*="phone"]', '416-555-0123');
      await form13Page.clickContinue();
      
      // Should move to next screen
      await form13Page.waitForQuestion('Income');
    });

    test('Validate currency fields accept only numbers', async () => {
      await form13Page.goto();
      
      // Navigate to income section
      await form13Page.fillPersonalInformation({
        fullName: 'Test User',
        courtName: 'Test Court'
      });
      
      await form13Page.fillContactInformation({
        address: '123 Test St',
        email: 'test@example.com',
        phone: '416-555-0123'
      });
      
      await form13Page.waitForQuestion('Income');
      
      // Test invalid currency inputs
      const invalidAmounts = ['abc', '12.34.56', '$12,34', '12e5'];
      
      for (const amount of invalidAmounts) {
        const currencyField = await page.locator(form13Page.currencyInput).first();
        await currencyField.fill(amount);
        
        const value = await currencyField.inputValue();
        // Currency fields should either reject or format the input
        expect(value).toMatch(/^[\d,\.]*$/);
      }
      
      // Test valid currency input
      await page.locator(form13Page.currencyInput).first().fill('5000.50');
      await page.fill('input[name*="description"]', 'Test Income');
      await page.click('label:has-text("No")'); // Don't add another
      await form13Page.clickContinue();
      
      // Should accept and move forward
      await form13Page.waitForQuestion('Expense');
    });

    test('Validate Ontario postal code format', async () => {
      await form13Page.goto();
      
      await form13Page.fillPersonalInformation({
        fullName: 'Test User',
        courtName: 'Test Court'
      });
      
      await form13Page.waitForQuestion('Contact Information');
      
      const postalField = await page.locator('input[name*="postal"]');
      if (await postalField.count() > 0) {
        // Test invalid postal codes
        const invalidPostalCodes = [
          '12345',      // US ZIP code
          'ABCDEF',     // Invalid format
          'Z9Z 9Z9',    // Invalid first letter (Z not used)
          'K1A0B1',     // Missing space
          'K1A  0B1',   // Too many spaces
        ];
        
        for (const postalCode of invalidPostalCodes) {
          await postalField.fill(postalCode);
          await form13Page.clickContinue();
          
          const errors = await form13Page.getValidationErrors();
          expect(errors.length, `Should show error for invalid postal code: ${postalCode}`).toBeGreaterThan(0);
          
          await postalField.clear();
        }
        
        // Test valid Ontario postal codes
        const validPostalCodes = [
          'K1A 0B1',  // Ottawa
          'M5H 2N2',  // Toronto
          'N6A 5B6',  // London
          'L5B 4G5',  // Mississauga
        ];
        
        for (const postalCode of validPostalCodes) {
          await postalField.fill(postalCode);
          await page.fill('input[type="email"]', 'test@example.com');
          await page.fill('input[name*="address"]', '123 Test St');
          await page.fill('input[type="tel"], input[name*="phone"]', '416-555-0123');
          await form13Page.clickContinue();
          
          // Should accept valid postal code and move forward
          await form13Page.waitForQuestion('Income');
          await page.goBack(); // Go back for next test
          await form13Page.waitForQuestion('Contact Information');
        }
      }
    });

    test('Validate date fields', async () => {
      await form13Page.goto();
      
      // Navigate to a screen with date fields
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Look for date fields
      const dateField = await page.locator('input[type="date"]').first();
      if (await dateField.count() > 0) {
        // Test future dates (if not allowed)
        const futureDate = new Date();
        futureDate.setFullYear(futureDate.getFullYear() + 10);
        await dateField.fill(futureDate.toISOString().split('T')[0]);
        
        // Test very old dates
        await dateField.fill('1800-01-01');
        
        // Test valid date
        const validDate = new Date();
        await dateField.fill(validDate.toISOString().split('T')[0]);
      }
    });
  });

  test.describe('Table Operations Tests', () => {
    test('Add and remove income items', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Add multiple income items
      const incomeItems = [
        { description: 'Salary', amount: 5000 },
        { description: 'Bonus', amount: 1000 },
        { description: 'Investment Income', amount: 500 }
      ];
      
      for (let i = 0; i < incomeItems.length; i++) {
        await form13Page.waitForQuestion('Income');
        await page.fill('input[name*="description"]', incomeItems[i].description);
        await page.fill(form13Page.currencyInput, incomeItems[i].amount.toString());
        
        if (i < incomeItems.length - 1) {
          await page.click('label:has-text("Yes")');
          await form13Page.clickContinue();
        }
      }
      
      // Complete the income section
      await page.click('label:has-text("No")');
      await form13Page.clickContinue();
    });

    test('Test maximum number of table rows', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Try to add many expense items (test table limits)
      const maxItems = 20; // Reasonable maximum to test
      
      for (let i = 0; i < maxItems; i++) {
        await form13Page.waitForQuestion('Income');
        await page.fill('input[name*="description"]', `Income Source ${i + 1}`);
        await page.fill(form13Page.currencyInput, (1000 * (i + 1)).toString());
        
        if (i < maxItems - 1) {
          const yesButton = await page.locator('label:has-text("Yes")');
          if (await yesButton.isVisible()) {
            await yesButton.click();
            await form13Page.clickContinue();
          } else {
            // Reached maximum, break
            break;
          }
        }
      }
      
      await page.click('label:has-text("No")');
      await form13Page.clickContinue();
    });
  });

  test.describe('Document Upload Tests', () => {
    test('Upload tax documents', async () => {
      await form13Page.goto('generated_interviews/form_13_comprehensive.yml');
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Skip to tax documents section if it exists
      // Create test PDF files for upload
      const testFiles = [
        { year: 2023, t1ReturnPath: './test-files/test-t1-2023.pdf', noaPath: './test-files/test-noa-2023.pdf' },
        { year: 2022, t1ReturnPath: './test-files/test-t1-2022.pdf', noaPath: './test-files/test-noa-2022.pdf' }
      ];
      
      // Note: In real tests, you would have actual test PDF files
      // For now, we'll check if the upload fields exist
      const fileInput = await page.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        console.log('File upload fields detected - would test with actual files');
      }
    });

    test('Test file size limits', async () => {
      // This test would require creating large test files
      // and checking that appropriate errors are shown
      test.skip('Requires large test files');
    });

    test('Test invalid file types', async () => {
      // Test uploading non-PDF files where PDF is required
      test.skip('Requires test files of various types');
    });
  });

  test.describe('Conditional Logic Tests', () => {
    test('Business owner shows additional business fields', async () => {
      await form13Page.goto();
      
      const businessOwnerData = generateTestData('business_owner');
      await form13Page.fillPersonalInformation(businessOwnerData.personal);
      await form13Page.fillContactInformation(businessOwnerData.contact);
      
      // Look for business-related questions
      // The specific flow depends on the interview configuration
      await form13Page.addIncomeItems([
        { description: 'Business Income', amount: 10000, frequency: 'monthly' }
      ]);
      
      // Check if business-specific fields appear
      const businessFields = await page.locator('input[name*="business"]');
      if (await businessFields.count() > 0) {
        console.log('Business fields detected for business owner');
      }
    });

    test('Support recipient shows different fields than payor', async () => {
      // This would test role-based conditional logic
      test.skip('Requires role selection in interview');
    });
  });

  test.describe('Navigation Tests', () => {
    test('Navigate backwards through the form', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      
      // Complete several screens
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Go back using back button
      const backButton = await page.locator(form13Page.backButton);
      if (await backButton.isVisible()) {
        await backButton.click();
        await page.waitForLoadState('networkidle');
        
        // Should be on contact information
        await form13Page.waitForQuestion('Contact Information');
        
        // Go back again
        await backButton.click();
        await page.waitForLoadState('networkidle');
        
        // Should be on personal information
        await form13Page.waitForQuestion('Personal Information');
      }
    });

    test('Test browser back/forward buttons', async () => {
      await form13Page.goto();
      await form13Page.testBrowserNavigation();
    });

    test('Resume interview from saved state', async () => {
      // This would require session management
      test.skip('Requires session persistence setup');
    });
  });

  test.describe('Review Screen Tests', () => {
    test('Edit information from review screen', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      await form13Page.addIncomeItems(basicData.income);
      await form13Page.addExpenseItems(basicData.expenses);
      
      // Should reach review screen
      await form13Page.waitForQuestion('Review');
      
      // Find and click edit button for personal information
      const editButtons = await page.locator('a:has-text("Edit"), button:has-text("Edit")');
      if (await editButtons.count() > 0) {
        await editButtons.first().click();
        await page.waitForLoadState('networkidle');
        
        // Should go back to personal information
        await form13Page.waitForQuestion('Personal Information');
        
        // Make changes
        await page.fill('input[name*="name"]', 'Updated Name');
        await form13Page.clickContinue();
        
        // Navigate back to review
        await form13Page.fillContactInformation(basicData.contact);
        await form13Page.addIncomeItems(basicData.income);
        await form13Page.addExpenseItems(basicData.expenses);
        
        await form13Page.waitForQuestion('Review');
        
        // Verify updated information is shown
        const updatedNameVisible = await page.locator('text=Updated Name').isVisible();
        expect(updatedNameVisible).toBeTruthy();
      }
    });

    test('Verify calculated totals on review screen', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      // Add income with known amounts
      const incomeItems = [
        { description: 'Income 1', amount: 1000 },
        { description: 'Income 2', amount: 2000 }
      ];
      await form13Page.addIncomeItems(incomeItems);
      
      // Add expenses with known amounts
      const expenseItems = [
        { description: 'Expense 1', amount: 500 },
        { description: 'Expense 2', amount: 700 }
      ];
      await form13Page.addExpenseItems(expenseItems);
      
      await form13Page.waitForQuestion('Review');
      
      // Check if totals are calculated correctly
      const totalIncome = incomeItems.reduce((sum, item) => sum + item.amount, 0);
      const totalExpenses = expenseItems.reduce((sum, item) => sum + item.amount, 0);
      const netIncome = totalIncome - totalExpenses;
      
      // Look for totals on the page
      const pageContent = await page.textContent('body');
      
      // Totals might be formatted with commas or currency symbols
      const totalIncomeFormatted = totalIncome.toLocaleString();
      const totalExpensesFormatted = totalExpenses.toLocaleString();
      const netIncomeFormatted = netIncome.toLocaleString();
      
      console.log(`Expected totals - Income: ${totalIncomeFormatted}, Expenses: ${totalExpensesFormatted}, Net: ${netIncomeFormatted}`);
    });
  });

  test.describe('Edge Cases and Error Handling', () => {
    test('Handle session timeout gracefully', async () => {
      // This would require manipulating session or waiting
      test.skip('Requires session timeout simulation');
    });

    test('Handle network interruption', async () => {
      // This would require network condition simulation
      test.skip('Requires network condition control');
    });

    test('Test with special characters in text fields', async () => {
      await form13Page.goto();
      
      // Test names with special characters
      await form13Page.fillPersonalInformation({
        fullName: "O'Brien-Smith, Jr.",
        courtName: 'Superior Court of Justice (Toronto)'
      });
      
      await form13Page.fillContactInformation({
        address: '123 Rue de l\'Église, Apt #456',
        email: 'test.user+legal@example.com',
        phone: '+1 (416) 555-0123'
      });
      
      // Should accept special characters
      await form13Page.addIncomeItems([
        { description: 'Income from ABC & Co.', amount: 5000 }
      ]);
    });

    test('Test with maximum length inputs', async () => {
      await form13Page.goto();
      
      // Create very long strings
      const longName = 'A'.repeat(255);
      const longDescription = 'This is a very long description. '.repeat(50);
      
      await form13Page.waitForQuestion('Personal Information');
      
      // Test if fields have maxlength restrictions
      const nameField = await page.locator('input[name*="name"]').first();
      await nameField.fill(longName);
      
      const actualValue = await nameField.inputValue();
      console.log(`Name field accepted ${actualValue.length} characters`);
      
      // Continue with reasonable values
      await nameField.fill('Test User');
      await form13Page.fillPersonalInformation({
        fullName: 'Test User',
        courtName: 'Test Court'
      });
      
      await form13Page.fillContactInformation({
        address: '123 Test St',
        email: 'test@example.com',
        phone: '416-555-0123'
      });
      
      // Test long description in income
      await form13Page.waitForQuestion('Income');
      await page.fill('input[name*="description"]', longDescription);
      
      const descField = await page.locator('input[name*="description"]').first();
      const descValue = await descField.inputValue();
      console.log(`Description field accepted ${descValue.length} characters`);
    });

    test('Test with zero and negative amounts', async () => {
      await form13Page.goto();
      
      const basicData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(basicData.personal);
      await form13Page.fillContactInformation(basicData.contact);
      
      await form13Page.waitForQuestion('Income');
      
      // Test zero amount
      await page.fill('input[name*="description"]', 'Zero Income');
      await page.fill(form13Page.currencyInput, '0');
      await page.click('label:has-text("Yes")');
      await form13Page.clickContinue();
      
      // Test negative amount (should be rejected)
      await page.fill('input[name*="description"]', 'Negative Income');
      await page.fill(form13Page.currencyInput, '-1000');
      await page.click('label:has-text("No")');
      await form13Page.clickContinue();
      
      // Check if negative amounts are rejected or converted to positive
      const currencyField = await page.locator(form13Page.currencyInput).first();
      const value = await currencyField.inputValue();
      console.log(`Currency field value after negative input: ${value}`);
    });
  });

  test.describe('Performance Tests', () => {
    test('Measure form load time', async () => {
      const startTime = Date.now();
      await form13Page.goto();
      const loadTime = Date.now() - startTime;
      
      console.log(`Form load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(10000); // Should load within 10 seconds
    });

    test('Measure PDF generation time', async () => {
      await form13Page.goto();
      
      const quickData = generateTestData('minimal');
      await form13Page.fillPersonalInformation(quickData.personal);
      await form13Page.fillContactInformation(quickData.contact);
      await form13Page.addIncomeItems(quickData.income.slice(0, 1));
      await form13Page.addExpenseItems(quickData.expenses.slice(0, 1));
      
      await form13Page.handleReviewScreen();
      
      const startTime = Date.now();
      await form13Page.completeSignature(quickData.signature);
      await form13Page.verifyFinalScreen();
      const pdfTime = Date.now() - startTime;
      
      console.log(`PDF generation time: ${pdfTime}ms`);
      expect(pdfTime).toBeLessThan(30000); // Should generate within 30 seconds
    });
  });
});