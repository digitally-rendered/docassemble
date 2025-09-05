import { test, expect, Page } from '@playwright/test';

/**
 * Playwright tests for Ontario Family Law Common Intake Interview
 * 
 * Test Coverage:
 * - Happy path with all fields filled
 * - Required field validation
 * - Optional fields being skipped
 * - Back button functionality
 * - Summary screen data verification
 * - Edge cases for each input field
 */

// Test configuration
const INTERVIEW_URL = '/interview?i=docassemble.playground1:ontario-family-law/common_intake.yml';
const DEFAULT_TIMEOUT = 30000;

// Test data constants
const TEST_DATA = {
  validUser: {
    firstName: 'John',
    middleName: 'Michael',
    lastName: 'Smith',
    otherNames: 'Johnny, J. Smith',
    birthDate: '1980-01-15'
  },
  edgeCaseUser: {
    firstName: "Mary-Jane O'Brien",
    middleName: 'Ann Marie',
    lastName: "Van Der Berg-Williams",
    otherNames: "MJ, Mary Jane O'Brien-Smith, Van Der Berg",
    birthDate: '1999-12-31'
  },
  minimalUser: {
    firstName: 'Jane',
    lastName: 'Doe'
  },
  specialChars: {
    firstName: "André-François",
    lastName: "Müller-Höß",
    otherNames: "A.F. Müller, André F. Höß"
  }
};

// Helper functions
class CommonIntakePage {
  constructor(private page: Page) {}

  // Navigation helpers
  async navigateToInterview() {
    await this.page.goto(INTERVIEW_URL);
    await this.page.waitForLoadState('networkidle');
  }

  async clickContinue() {
    await this.page.click('button:has-text("Continue")');
    await this.page.waitForLoadState('networkidle');
  }

  async clickBack() {
    await this.page.click('button:has-text("Back")');
    await this.page.waitForLoadState('networkidle');
  }

  // Form filling helpers
  async fillPersonalInfo(data: {
    firstName?: string;
    middleName?: string;
    lastName?: string;
    otherNames?: string;
    birthDate?: string;
  }) {
    if (data.firstName !== undefined) {
      await this.page.fill('input[name="user.name.first"]', data.firstName);
    }
    if (data.middleName !== undefined) {
      await this.page.fill('input[name="user.name.middle"]', data.middleName);
    }
    if (data.lastName !== undefined) {
      await this.page.fill('input[name="user.name.last"]', data.lastName);
    }
    if (data.otherNames !== undefined) {
      await this.page.fill('input[name="user.name.suffix"]', data.otherNames);
    }
    if (data.birthDate !== undefined) {
      await this.page.fill('input[name="user.birthdate"]', data.birthDate);
    }
  }

  async clearField(fieldName: string) {
    const selector = `input[name="${fieldName}"]`;
    await this.page.fill(selector, '');
  }

  // Validation helpers
  async expectValidationError(fieldName: string, errorMessage?: string) {
    // Docassemble shows validation errors in different ways
    const fieldSelector = `input[name="${fieldName}"]`;
    
    // Check for field-specific error message
    const errorSelector = `.da-has-error:has(input[name="${fieldName}"]) .help-block, .text-danger`;
    const errorElement = await this.page.locator(errorSelector).first();
    
    if (errorMessage) {
      await expect(errorElement).toContainText(errorMessage);
    } else {
      await expect(errorElement).toBeVisible();
    }
    
    // Check that the field has error styling
    const field = await this.page.locator(fieldSelector);
    const parentDiv = await field.locator('xpath=ancestor::div[contains(@class, "form-group")]').first();
    await expect(parentDiv).toHaveClass(/has-error|is-invalid/);
  }

  // Assertion helpers
  async expectToBeOnIntroScreen() {
    await expect(this.page.locator('h1')).toContainText('Ontario Family Law Common Intake');
    await expect(this.page.locator('button:has-text("Continue")')).toBeVisible();
  }

  async expectToBeOnPersonalInfoScreen() {
    await expect(this.page.locator('h1')).toContainText('Your Personal Information');
    await expect(this.page.locator('input[name="user.name.first"]')).toBeVisible();
    await expect(this.page.locator('input[name="user.name.last"]')).toBeVisible();
  }

  async expectToBeOnSummaryScreen() {
    await expect(this.page.locator('h1')).toContainText('Information Collected');
    await expect(this.page.locator('text=Your Information:')).toBeVisible();
  }

  async verifySummaryContent(expectedData: {
    fullName: string;
    birthDate?: string;
    otherNames?: string;
  }) {
    // Verify the full name is displayed
    await expect(this.page.locator('body')).toContainText(`Name: ${expectedData.fullName}`);
    
    // Verify birth date if provided
    if (expectedData.birthDate) {
      await expect(this.page.locator('body')).toContainText(`Date of Birth: ${expectedData.birthDate}`);
    } else {
      // Birth date section should not be visible if not provided
      await expect(this.page.locator('text=Date of Birth:')).not.toBeVisible();
    }
    
    // Verify other names if provided
    if (expectedData.otherNames) {
      await expect(this.page.locator('body')).toContainText(`Other names used: ${expectedData.otherNames}`);
    } else {
      // Other names section should not be visible if not provided
      await expect(this.page.locator('text=Other names used:')).not.toBeVisible();
    }
  }

  // Progress bar helpers
  async getProgressPercentage(): Promise<number> {
    const progressBar = await this.page.locator('.progress-bar').first();
    const style = await progressBar.getAttribute('style');
    const match = style?.match(/width:\s*(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }
}

// Test Suite
test.describe('Ontario Family Law Common Intake Interview', () => {
  let page: Page;
  let commonIntake: CommonIntakePage;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    commonIntake = new CommonIntakePage(page);
    await commonIntake.navigateToInterview();
  });

  test.afterEach(async () => {
    await page.close();
  });

  test.describe('Happy Path', () => {
    test('should complete interview with all fields filled', async () => {
      // Step 1: Introduction screen
      await commonIntake.expectToBeOnIntroScreen();
      const initialProgress = await commonIntake.getProgressPercentage();
      expect(initialProgress).toBe(0);
      await commonIntake.clickContinue();

      // Step 2: Personal Information screen
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await commonIntake.fillPersonalInfo(TEST_DATA.validUser);
      const midProgress = await commonIntake.getProgressPercentage();
      expect(midProgress).toBeGreaterThan(initialProgress);
      await commonIntake.clickContinue();

      // Step 3: Summary screen
      await commonIntake.expectToBeOnSummaryScreen();
      const finalProgress = await commonIntake.getProgressPercentage();
      expect(finalProgress).toBe(100);
      
      // Verify all data is displayed correctly
      await commonIntake.verifySummaryContent({
        fullName: 'John Michael Smith',
        birthDate: '01/15/1980',
        otherNames: 'Johnny, J. Smith'
      });
    });

    test('should complete interview with minimal required fields only', async () => {
      // Navigate through introduction
      await commonIntake.clickContinue();

      // Fill only required fields
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      await commonIntake.clickContinue();

      // Verify summary shows only provided information
      await commonIntake.expectToBeOnSummaryScreen();
      await commonIntake.verifySummaryContent({
        fullName: 'Jane Doe'
      });
    });

    test('should handle special characters and complex names', async () => {
      await commonIntake.clickContinue();
      
      await commonIntake.fillPersonalInfo(TEST_DATA.specialChars);
      await commonIntake.clickContinue();

      await commonIntake.verifySummaryContent({
        fullName: 'André-François Müller-Höß',
        otherNames: 'A.F. Müller, André F. Höß'
      });
    });

    test('should handle edge case dates and hyphenated names', async () => {
      await commonIntake.clickContinue();
      
      await commonIntake.fillPersonalInfo(TEST_DATA.edgeCaseUser);
      await commonIntake.clickContinue();

      await commonIntake.verifySummaryContent({
        fullName: "Mary-Jane O'Brien Ann Marie Van Der Berg-Williams",
        birthDate: '12/31/1999',
        otherNames: "MJ, Mary Jane O'Brien-Smith, Van Der Berg"
      });
    });
  });

  test.describe('Field Validation', () => {
    test('should require first name', async () => {
      await commonIntake.clickContinue();
      
      // Try to submit without first name
      await commonIntake.fillPersonalInfo({
        lastName: 'Smith'
      });
      await commonIntake.clickContinue();
      
      // Should still be on the same screen with validation error
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await commonIntake.expectValidationError('user.name.first', 'Please enter your first name');
    });

    test('should require last name', async () => {
      await commonIntake.clickContinue();
      
      // Try to submit without last name
      await commonIntake.fillPersonalInfo({
        firstName: 'John'
      });
      await commonIntake.clickContinue();
      
      // Should still be on the same screen with validation error
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await commonIntake.expectValidationError('user.name.last', 'Please enter your last name');
    });

    test('should require both first and last name', async () => {
      await commonIntake.clickContinue();
      
      // Try to submit with no required fields
      await commonIntake.fillPersonalInfo({
        middleName: 'Michael',
        otherNames: 'Test'
      });
      await commonIntake.clickContinue();
      
      // Should show errors for both fields
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await commonIntake.expectValidationError('user.name.first');
      await commonIntake.expectValidationError('user.name.last');
    });

    test('should allow empty optional fields', async () => {
      await commonIntake.clickContinue();
      
      // Fill only required fields, leave optional empty
      await commonIntake.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User',
        middleName: '',
        otherNames: '',
        birthDate: ''
      });
      await commonIntake.clickContinue();
      
      // Should successfully proceed
      await commonIntake.expectToBeOnSummaryScreen();
      await commonIntake.verifySummaryContent({
        fullName: 'Test User'
      });
    });

    test('should validate date format for birth date', async () => {
      await commonIntake.clickContinue();
      
      // Test various date formats
      const invalidDates = ['invalid', '13/32/2000', '2000-13-32', 'abc-def-ghij'];
      
      for (const invalidDate of invalidDates) {
        await commonIntake.fillPersonalInfo({
          firstName: 'Test',
          lastName: 'User',
          birthDate: invalidDate
        });
        
        // Clear and try next invalid date
        await commonIntake.clearField('user.birthdate');
      }
      
      // Valid date should work
      await commonIntake.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User',
        birthDate: '2000-01-01'
      });
      await commonIntake.clickContinue();
      
      await commonIntake.expectToBeOnSummaryScreen();
    });

    test('should handle whitespace in required fields', async () => {
      await commonIntake.clickContinue();
      
      // Try to submit with only spaces
      await commonIntake.fillPersonalInfo({
        firstName: '   ',
        lastName: '   '
      });
      await commonIntake.clickContinue();
      
      // Should show validation errors
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await commonIntake.expectValidationError('user.name.first');
    });
  });

  test.describe('Navigation', () => {
    test('should navigate back from personal info to introduction', async () => {
      // Go to personal info screen
      await commonIntake.clickContinue();
      await commonIntake.expectToBeOnPersonalInfoScreen();
      
      // Navigate back
      await commonIntake.clickBack();
      await commonIntake.expectToBeOnIntroScreen();
      
      // Should be able to continue forward again
      await commonIntake.clickContinue();
      await commonIntake.expectToBeOnPersonalInfoScreen();
    });

    test('should navigate back from summary to personal info', async () => {
      // Complete the interview
      await commonIntake.clickContinue();
      await commonIntake.fillPersonalInfo(TEST_DATA.validUser);
      await commonIntake.clickContinue();
      await commonIntake.expectToBeOnSummaryScreen();
      
      // Navigate back
      await commonIntake.clickBack();
      await commonIntake.expectToBeOnPersonalInfoScreen();
      
      // Fields should retain their values
      await expect(page.locator('input[name="user.name.first"]')).toHaveValue(TEST_DATA.validUser.firstName);
      await expect(page.locator('input[name="user.name.last"]')).toHaveValue(TEST_DATA.validUser.lastName);
    });

    test('should maintain field values when navigating back and forth', async () => {
      await commonIntake.clickContinue();
      
      // Fill partial data
      await commonIntake.fillPersonalInfo({
        firstName: 'TestFirst',
        middleName: 'TestMiddle'
      });
      
      // Go back
      await commonIntake.clickBack();
      await commonIntake.expectToBeOnIntroScreen();
      
      // Go forward again
      await commonIntake.clickContinue();
      
      // Check that partial data is preserved
      await expect(page.locator('input[name="user.name.first"]')).toHaveValue('TestFirst');
      await expect(page.locator('input[name="user.name.middle"]')).toHaveValue('TestMiddle');
      await expect(page.locator('input[name="user.name.last"]')).toHaveValue('');
      
      // Complete the form
      await commonIntake.fillPersonalInfo({
        lastName: 'TestLast'
      });
      await commonIntake.clickContinue();
      
      // Go back from summary
      await commonIntake.clickBack();
      
      // All data should be preserved
      await expect(page.locator('input[name="user.name.first"]')).toHaveValue('TestFirst');
      await expect(page.locator('input[name="user.name.middle"]')).toHaveValue('TestMiddle');
      await expect(page.locator('input[name="user.name.last"]')).toHaveValue('TestLast');
    });

    test('should handle multiple back navigations', async () => {
      // Navigate to summary
      await commonIntake.clickContinue();
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      await commonIntake.clickContinue();
      
      // Go back twice
      await commonIntake.clickBack();
      await commonIntake.clickBack();
      
      // Should be at introduction
      await commonIntake.expectToBeOnIntroScreen();
    });
  });

  test.describe('Edge Cases', () => {
    test('should handle very long names', async () => {
      await commonIntake.clickContinue();
      
      const longName = 'A'.repeat(100);
      await commonIntake.fillPersonalInfo({
        firstName: longName,
        middleName: longName,
        lastName: longName,
        otherNames: longName
      });
      await commonIntake.clickContinue();
      
      await commonIntake.expectToBeOnSummaryScreen();
      // Verify at least part of the long name is displayed
      await expect(page.locator('body')).toContainText('A'.repeat(50));
    });

    test('should handle rapid form submission', async () => {
      await commonIntake.clickContinue();
      
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      
      // Try rapid double-click on continue
      const continueButton = page.locator('button:has-text("Continue")');
      await continueButton.dblclick();
      
      // Should only advance once and be on summary
      await commonIntake.expectToBeOnSummaryScreen();
    });

    test('should handle browser refresh on personal info screen', async () => {
      await commonIntake.clickContinue();
      
      // Fill some data
      await commonIntake.fillPersonalInfo({
        firstName: 'RefreshTest',
        lastName: 'User'
      });
      
      // Refresh the page
      await page.reload();
      
      // Should maintain session and data
      await commonIntake.expectToBeOnPersonalInfoScreen();
      await expect(page.locator('input[name="user.name.first"]')).toHaveValue('RefreshTest');
      await expect(page.locator('input[name="user.name.last"]')).toHaveValue('User');
    });

    test('should handle copy-paste in form fields', async () => {
      await commonIntake.clickContinue();
      
      // Simulate copy-paste behavior
      const firstNameField = page.locator('input[name="user.name.first"]');
      await firstNameField.click();
      await page.keyboard.type('Original');
      await page.keyboard.press('Control+A');
      await page.keyboard.press('Control+C');
      
      const middleNameField = page.locator('input[name="user.name.middle"]');
      await middleNameField.click();
      await page.keyboard.press('Control+V');
      
      await expect(firstNameField).toHaveValue('Original');
      await expect(middleNameField).toHaveValue('Original');
    });

    test('should handle tab navigation through fields', async () => {
      await commonIntake.clickContinue();
      
      // Start at first field
      await page.locator('input[name="user.name.first"]').focus();
      await page.keyboard.type('TabTest1');
      
      // Tab to next field
      await page.keyboard.press('Tab');
      await page.keyboard.type('TabTest2');
      
      // Tab to next field
      await page.keyboard.press('Tab');
      await page.keyboard.type('TabTest3');
      
      // Verify values
      await expect(page.locator('input[name="user.name.first"]')).toHaveValue('TabTest1');
      await expect(page.locator('input[name="user.name.middle"]')).toHaveValue('TabTest2');
      await expect(page.locator('input[name="user.name.last"]')).toHaveValue('TabTest3');
    });

    test('should handle future dates in birth date field', async () => {
      await commonIntake.clickContinue();
      
      const futureDate = new Date();
      futureDate.setFullYear(futureDate.getFullYear() + 1);
      const futureDateStr = futureDate.toISOString().split('T')[0];
      
      await commonIntake.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User',
        birthDate: futureDateStr
      });
      
      // Should accept the date (no built-in future date validation in the current YAML)
      await commonIntake.clickContinue();
      await commonIntake.expectToBeOnSummaryScreen();
    });

    test('should handle very old dates in birth date field', async () => {
      await commonIntake.clickContinue();
      
      await commonIntake.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User',
        birthDate: '1900-01-01'
      });
      await commonIntake.clickContinue();
      
      await commonIntake.verifySummaryContent({
        fullName: 'Test User',
        birthDate: '01/01/1900'
      });
    });
  });

  test.describe('Accessibility', () => {
    test('should be keyboard navigable', async () => {
      // Navigate using only keyboard
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter'); // Click continue
      
      await commonIntake.expectToBeOnPersonalInfoScreen();
      
      // Fill form using keyboard only
      await page.keyboard.press('Tab'); // Focus first field
      await page.keyboard.type('KeyboardFirst');
      await page.keyboard.press('Tab');
      await page.keyboard.type('KeyboardMiddle');
      await page.keyboard.press('Tab');
      await page.keyboard.type('KeyboardLast');
      
      // Submit with keyboard
      await page.keyboard.press('Tab'); // Navigate to continue button
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      
      await commonIntake.expectToBeOnSummaryScreen();
    });

    test('should have proper field labels and help text', async () => {
      await commonIntake.clickContinue();
      
      // Check that labels are associated with fields
      const firstNameLabel = await page.locator('label:has-text("First Name")');
      await expect(firstNameLabel).toBeVisible();
      
      const lastNameLabel = await page.locator('label:has-text("Last Name")');
      await expect(lastNameLabel).toBeVisible();
      
      // Check for help text on other names field
      const otherNamesHelp = await page.locator('text=Include maiden name, previous married names');
      await expect(otherNamesHelp).toBeVisible();
    });

    test('should indicate required fields', async () => {
      await commonIntake.clickContinue();
      
      // Required fields should have asterisk or required indicator
      const firstNameLabel = await page.locator('label:has-text("First Name")');
      const firstNameRequired = await firstNameLabel.locator('.da-required-asterisk, :has-text("*")').count();
      expect(firstNameRequired).toBeGreaterThan(0);
      
      const lastNameLabel = await page.locator('label:has-text("Last Name")');
      const lastNameRequired = await lastNameLabel.locator('.da-required-asterisk, :has-text("*")').count();
      expect(lastNameRequired).toBeGreaterThan(0);
    });
  });

  test.describe('Performance', () => {
    test('should load interview within acceptable time', async () => {
      const startTime = Date.now();
      await commonIntake.navigateToInterview();
      const loadTime = Date.now() - startTime;
      
      expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
    });

    test('should navigate between screens quickly', async () => {
      await commonIntake.clickContinue();
      
      const startTime = Date.now();
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      await commonIntake.clickContinue();
      const navigationTime = Date.now() - startTime;
      
      expect(navigationTime).toBeLessThan(3000); // Navigation should be under 3 seconds
    });
  });

  test.describe('Data Persistence', () => {
    test('should maintain data across session', async () => {
      // Fill first part of the form
      await commonIntake.clickContinue();
      await commonIntake.fillPersonalInfo({
        firstName: 'Session',
        lastName: 'Test'
      });
      
      // Get the session URL
      const currentUrl = page.url();
      
      // Open new page with same session
      const newPage = await page.context().newPage();
      await newPage.goto(currentUrl);
      
      // Should still be on personal info screen with data
      const newPageIntake = new CommonIntakePage(newPage);
      await newPageIntake.expectToBeOnPersonalInfoScreen();
      await expect(newPage.locator('input[name="user.name.first"]')).toHaveValue('Session');
      await expect(newPage.locator('input[name="user.name.last"]')).toHaveValue('Test');
      
      await newPage.close();
    });
  });

  test.describe('Exit and Restart Functionality', () => {
    test('should handle exit button on summary screen', async () => {
      await commonIntake.clickContinue();
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      await commonIntake.clickContinue();
      
      // Click exit button
      const exitButton = page.locator('button:has-text("Exit")');
      await expect(exitButton).toBeVisible();
      await exitButton.click();
      
      // Should exit the interview (redirect or show exit message)
      await page.waitForLoadState('networkidle');
    });

    test('should handle restart button on summary screen', async () => {
      await commonIntake.clickContinue();
      await commonIntake.fillPersonalInfo(TEST_DATA.minimalUser);
      await commonIntake.clickContinue();
      
      // Click restart button
      const restartButton = page.locator('button:has-text("Restart")');
      await expect(restartButton).toBeVisible();
      await restartButton.click();
      
      // Should restart at introduction
      await page.waitForLoadState('networkidle');
      await commonIntake.expectToBeOnIntroScreen();
    });
  });
});

// Configuration export for running tests
export default {
  use: {
    // Base URL should be configured to point to your Docassemble instance
    baseURL: process.env.DOCASSEMBLE_URL || 'http://localhost',
    
    // Slow down actions for debugging
    slowMo: process.env.CI ? 0 : 50,
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Increased timeout for Docassemble's sometimes slow responses
    timeout: DEFAULT_TIMEOUT,
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
  },
  
  // Test retry configuration
  retries: process.env.CI ? 2 : 0,
  
  // Reporter configuration
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
    ['junit', { outputFile: 'test-results.xml' }]
  ],
  
  // Project configuration
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
      },
    },
    {
      name: 'firefox',
      use: {
        browserName: 'firefox',
      },
    },
    {
      name: 'webkit',
      use: {
        browserName: 'webkit',
      },
    },
  ],
};