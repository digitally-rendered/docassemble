// Base class for Ontario Family Law Form tests
import { test as base, expect } from '@playwright/test';
import { testData } from './test-data/ontario-test-data.js';

// Custom test fixture with common form functionality
export const test = base.extend({
  // Auto-login fixture
  autoLogin: async ({ page }, use) => {
    // Navigate to docassemble instance
    await page.goto(process.env.DOCASSEMBLE_URL || 'http://localhost');
    
    // Login if required
    if (await page.locator('input[name="email"]').isVisible()) {
      await page.fill('input[name="email"]', process.env.DOCASSEMBLE_EMAIL || 'admin@admin.com');
      await page.fill('input[name="password"]', process.env.DOCASSEMBLE_PASSWORD || 'password');
      await page.click('button[type="submit"]');
      await page.waitForLoadState('networkidle');
    }
    
    await use(page);
  },
  
  // Form navigation helpers
  formHelpers: async ({ page }, use) => {
    const helpers = {
      // Start a specific form interview
      startInterview: async (formName) => {
        const interviewUrl = `/interview?i=docassemble.playground1:${formName}`;
        await page.goto(interviewUrl);
        await page.waitForLoadState('networkidle');
      },
      
      // Continue to next page
      continueForm: async () => {
        const continueButton = page.locator('button:has-text("Continue")').first();
        await continueButton.click();
        await page.waitForLoadState('networkidle');
      },
      
      // Go back to previous page
      goBack: async () => {
        const backButton = page.locator('button:has-text("Back")').first();
        if (await backButton.isVisible()) {
          await backButton.click();
          await page.waitForLoadState('networkidle');
        }
      },
      
      // Fill text field
      fillTextField: async (fieldName, value) => {
        const field = page.locator(`input[name="${fieldName}"], textarea[name="${fieldName}"]`).first();
        await field.fill(value);
      },
      
      // Fill date field
      fillDateField: async (fieldName, date) => {
        const field = page.locator(`input[name="${fieldName}"]`).first();
        await field.fill(date);
      },
      
      // Fill currency field
      fillCurrencyField: async (fieldName, amount) => {
        const field = page.locator(`input[name="${fieldName}"]`).first();
        await field.fill(amount.toString());
      },
      
      // Select radio button
      selectRadio: async (fieldName, value) => {
        const radio = page.locator(`input[name="${fieldName}"][value="${value}"]`).first();
        await radio.check();
      },
      
      // Check checkbox
      checkBox: async (fieldName, check = true) => {
        const checkbox = page.locator(`input[name="${fieldName}"][type="checkbox"]`).first();
        if (check) {
          await checkbox.check();
        } else {
          await checkbox.uncheck();
        }
      },
      
      // Select from dropdown
      selectOption: async (fieldName, value) => {
        const select = page.locator(`select[name="${fieldName}"]`).first();
        await select.selectOption(value);
      },
      
      // Fill address block
      fillAddress: async (prefix, address) => {
        await helpers.fillTextField(`${prefix}_address`, address.street);
        await helpers.fillTextField(`${prefix}_city`, address.city);
        await helpers.fillTextField(`${prefix}_province`, address.province);
        await helpers.fillTextField(`${prefix}_postal_code`, address.postalCode);
      },
      
      // Fill person info block
      fillPersonInfo: async (prefix, person) => {
        await helpers.fillTextField(`${prefix}_first_name`, person.firstName);
        await helpers.fillTextField(`${prefix}_last_name`, person.lastName);
        if (person.middleName) {
          await helpers.fillTextField(`${prefix}_middle_name`, person.middleName);
        }
        await helpers.fillDateField(`${prefix}_date_of_birth`, person.dateOfBirth);
        await helpers.fillTextField(`${prefix}_phone`, person.phone);
        await helpers.fillTextField(`${prefix}_email`, person.email);
      },
      
      // Verify field validation error
      verifyValidationError: async (fieldName, errorText) => {
        const errorElement = page.locator(`.has-error:has(input[name="${fieldName}"]) .help-block`);
        await expect(errorElement).toContainText(errorText);
      },
      
      // Verify success message
      verifySuccessMessage: async (message) => {
        const successElement = page.locator('.alert-success');
        await expect(successElement).toContainText(message);
      },
      
      // Check if on specific page by title
      verifyPageTitle: async (expectedTitle) => {
        const title = page.locator('h1, .question-text').first();
        await expect(title).toContainText(expectedTitle);
      },
      
      // Save and resume later
      saveProgress: async () => {
        const saveButton = page.locator('button:has-text("Save and Resume Later")').first();
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await page.waitForLoadState('networkidle');
        }
      },
      
      // Download completed form
      downloadForm: async (format = 'pdf') => {
        const downloadButton = page.locator(`a:has-text("Download ${format.toUpperCase()}")`).first();
        const [download] = await Promise.all([
          page.waitForEvent('download'),
          downloadButton.click()
        ]);
        return download;
      },
      
      // Handle table/repeating fields
      addTableRow: async (tableName) => {
        const addButton = page.locator(`button:has-text("Add another"):near(table[data-table="${tableName}"])`).first();
        await addButton.click();
        await page.waitForLoadState('networkidle');
      },
      
      // Fill table cell
      fillTableCell: async (tableName, row, column, value) => {
        const cell = page.locator(`table[data-table="${tableName}"] tr:nth-child(${row + 1}) td:nth-child(${column + 1}) input`).first();
        await cell.fill(value);
      }
    };
    
    await use(helpers);
  }
});

// Common assertions for forms
export const formAssertions = {
  // Verify required fields are marked
  async verifyRequiredFields(page, fieldNames) {
    for (const fieldName of fieldNames) {
      const field = page.locator(`[name="${fieldName}"]`).first();
      const label = page.locator(`label[for="${fieldName}"]`).first();
      const requiredIndicator = label.locator('.required-indicator, .text-danger:has-text("*")');
      await expect(requiredIndicator).toBeVisible();
    }
  },
  
  // Verify form progress
  async verifyProgress(page, expectedPercentage) {
    const progressBar = page.locator('.progress-bar');
    const actualPercentage = await progressBar.getAttribute('aria-valuenow');
    expect(parseInt(actualPercentage)).toBeCloseTo(expectedPercentage, 5);
  },
  
  // Verify form completion
  async verifyFormComplete(page) {
    const completionMessage = page.locator('h1:has-text("Form Complete"), .alert-success:has-text("completed")');
    await expect(completionMessage).toBeVisible();
  },
  
  // Verify PDF generation
  async verifyPDFAvailable(page) {
    const pdfLink = page.locator('a[href$=".pdf"], a:has-text("Download PDF")');
    await expect(pdfLink).toBeVisible();
  }
};

// Common test scenarios
export const commonScenarios = {
  // Test field validation
  async testFieldValidation(page, helpers, fieldName, invalidValue, validValue, errorMessage) {
    await helpers.fillTextField(fieldName, invalidValue);
    await helpers.continueForm();
    await helpers.verifyValidationError(fieldName, errorMessage);
    await helpers.fillTextField(fieldName, validValue);
    await helpers.continueForm();
  },
  
  // Test required field
  async testRequiredField(page, helpers, fieldName) {
    await helpers.continueForm();
    await helpers.verifyValidationError(fieldName, 'This field is required');
  },
  
  // Test date field
  async testDateField(page, helpers, fieldName) {
    // Test invalid date
    await helpers.fillDateField(fieldName, '99/99/9999');
    await helpers.continueForm();
    await helpers.verifyValidationError(fieldName, 'Please enter a valid date');
    
    // Test future date (if not allowed)
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 1);
    await helpers.fillDateField(fieldName, futureDate.toISOString().split('T')[0]);
    await helpers.continueForm();
    
    // Test valid date
    await helpers.fillDateField(fieldName, '2024-01-15');
    await helpers.continueForm();
  },
  
  // Test email field
  async testEmailField(page, helpers, fieldName) {
    await commonScenarios.testFieldValidation(
      page,
      helpers,
      fieldName,
      'invalid-email',
      'test@example.com',
      'Please enter a valid email address'
    );
  },
  
  // Test phone field
  async testPhoneField(page, helpers, fieldName) {
    await commonScenarios.testFieldValidation(
      page,
      helpers,
      fieldName,
      '123',
      '(416) 555-1234',
      'Please enter a valid phone number'
    );
  },
  
  // Test postal code field
  async testPostalCodeField(page, helpers, fieldName) {
    await commonScenarios.testFieldValidation(
      page,
      helpers,
      fieldName,
      'INVALID',
      'M5H 2M9',
      'Please enter a valid Canadian postal code'
    );
  }
};

export { expect } from '@playwright/test';
export { testData } from './test-data/ontario-test-data.js';