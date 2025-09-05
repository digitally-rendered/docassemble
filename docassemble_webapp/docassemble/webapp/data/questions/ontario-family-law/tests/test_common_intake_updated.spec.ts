import { test, expect, Page } from '@playwright/test';

/**
 * Updated tests for the comprehensive Ontario Family Law Common Intake interview
 * Tests the full flow including lawyer info, opposing party, and court information
 */

// Helper class for page interactions
class CommonIntakePage {
  constructor(public page: Page) {}

  // Navigation methods
  async startInterview() {
    await this.page.goto('/interview?i=docassemble.webapp:ontario-family-law/common_intake.yml');
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

  async clickYes() {
    await this.page.click('input[value="True"]');
  }

  async clickNo() {
    await this.page.click('input[value="False"]');
  }

  // Fill form methods
  async fillPersonalInfo(data: {
    firstName: string;
    middleName?: string;
    lastName: string;
    otherNames?: string;
    birthdate?: string;
  }) {
    await this.page.fill('input[name*="name.first"]', data.firstName);
    if (data.middleName) {
      await this.page.fill('input[name*="name.middle"]', data.middleName);
    }
    await this.page.fill('input[name*="name.last"]', data.lastName);
    if (data.otherNames) {
      await this.page.fill('input[name*="name.suffix"]', data.otherNames);
    }
    if (data.birthdate) {
      await this.page.fill('input[name*="birthdate"]', data.birthdate);
    }
  }

  async fillContactInfo(data: {
    street: string;
    city: string;
    province?: string;
    postalCode: string;
    phone?: string;
    altPhone?: string;
    email?: string;
    preferredContact?: string;
  }) {
    await this.page.fill('input[name*="address.address"]', data.street);
    await this.page.fill('input[name*="address.city"]', data.city);
    if (data.province) {
      await this.page.selectOption('select[name*="address.state"]', data.province);
    }
    await this.page.fill('input[name*="address.postal_code"]', data.postalCode);
    if (data.phone) {
      await this.page.fill('input[name*="phone_number"]', data.phone);
    }
    if (data.altPhone) {
      await this.page.fill('input[name*="mobile_number"]', data.altPhone);
    }
    if (data.email) {
      await this.page.fill('input[name*="email"]', data.email);
    }
    if (data.preferredContact) {
      await this.page.selectOption('select[name*="contact_preference"]', data.preferredContact);
    }
  }

  async fillOpposingPartyInfo(data: {
    firstName: string;
    lastName: string;
    middleName?: string;
    street?: string;
    city?: string;
    province?: string;
    postalCode?: string;
    phone?: string;
    email?: string;
  }) {
    await this.page.fill('input[name*="opposing_party"][name*="name.first"]', data.firstName);
    await this.page.fill('input[name*="opposing_party"][name*="name.last"]', data.lastName);
    if (data.middleName) {
      await this.page.fill('input[name*="opposing_party"][name*="name.middle"]', data.middleName);
    }
    if (data.street) {
      await this.page.fill('input[name*="opposing_party"][name*="address.address"]', data.street);
    }
    if (data.city) {
      await this.page.fill('input[name*="opposing_party"][name*="address.city"]', data.city);
    }
    if (data.postalCode) {
      await this.page.fill('input[name*="opposing_party"][name*="address.postal_code"]', data.postalCode);
    }
    if (data.phone) {
      await this.page.fill('input[name*="opposing_party"][name*="phone_number"]', data.phone);
    }
    if (data.email) {
      await this.page.fill('input[name*="opposing_party"][name*="email"]', data.email);
    }
  }

  async fillCourtInfo(data: {
    hasFile: boolean;
    courtName?: string;
    location?: string;
    fileNumber?: string;
    region?: string;
    dateStarted?: string;
    proceedingType?: string;
  }) {
    // First question: Do you have an existing court file?
    if (data.hasFile) {
      await this.page.click('input[value="True"]');
      // Fill court details
      if (data.courtName) {
        await this.page.selectOption('select[name*="court.name"]', data.courtName);
      }
      if (data.location) {
        await this.page.fill('input[name*="court.location"]', data.location);
      }
      if (data.fileNumber) {
        await this.page.fill('input[name*="court.file_number"]', data.fileNumber);
      }
      if (data.region) {
        await this.page.selectOption('select[name*="court.judicial_region"]', data.region);
      }
      if (data.dateStarted) {
        await this.page.fill('input[name*="court.date_started"]', data.dateStarted);
      }
      if (data.proceedingType) {
        await this.page.selectOption('select[name*="court.proceeding_type"]', data.proceedingType);
      }
    } else {
      await this.page.click('input[value="False"]');
    }
  }
}

test.describe('Ontario Family Law Common Intake Interview - Full Flow', () => {
  let page: CommonIntakePage;

  test.beforeEach(async ({ page: playwrightPage }) => {
    page = new CommonIntakePage(playwrightPage);
    await page.startInterview();
  });

  test.describe('Complete Interview Flow', () => {
    test('should complete full interview with all information', async () => {
      // Introduction screen
      await expect(page.page).toHaveText(/Ontario Family Law Common Intake/);
      await page.clickContinue();

      // Personal Information
      await expect(page.page).toHaveText(/Your Personal Information/);
      await page.fillPersonalInfo({
        firstName: 'John',
        middleName: 'Michael',
        lastName: 'Smith',
        otherNames: 'Johnny',
        birthdate: '01/15/1980'
      });
      await page.clickContinue();

      // Contact Information
      await expect(page.page).toHaveText(/Your Contact Information/);
      await page.fillContactInfo({
        street: '123 Main Street',
        city: 'Toronto',
        province: 'Ontario',
        postalCode: 'M5H 2N2',
        phone: '416-555-1234',
        email: 'john.smith@example.com',
        preferredContact: 'Email'
      });
      await page.clickContinue();

      // Legal Representation
      await expect(page.page).toHaveText(/Legal Representation/);
      await page.clickNo(); // No lawyer
      await page.clickContinue();

      // Other Party's Information
      await expect(page.page).toHaveText(/Other Party's Information/);
      await page.fillOpposingPartyInfo({
        firstName: 'Jane',
        lastName: 'Doe',
        street: '456 Oak Avenue',
        city: 'Toronto',
        postalCode: 'M4C 1A1',
        phone: '416-555-5678',
        email: 'jane.doe@example.com'
      });
      await page.clickContinue();

      // Other Party's Legal Representation
      await expect(page.page).toHaveText(/Other Party's Legal Representation/);
      await page.clickNo(); // They don't have a lawyer
      await page.clickContinue();

      // Court Information
      await expect(page.page).toHaveText(/Court Information/);
      await page.fillCourtInfo({
        hasFile: true,
        courtName: 'Superior Court of Justice',
        location: 'Toronto',
        fileNumber: 'CV-21-123456',
        region: 'Toronto',
        proceedingType: 'Divorce'
      });
      await page.clickContinue();

      // Summary screen
      await expect(page.page).toHaveText(/Information Collected/);
      await expect(page.page).toHaveText(/John Michael Smith/);
      await expect(page.page).toHaveText(/123 Main Street/);
      await expect(page.page).toHaveText(/416-555-1234/);
      await expect(page.page).toHaveText(/Self-represented/);
      await expect(page.page).toHaveText(/Jane Doe/);
      await expect(page.page).toHaveText(/CV-21-123456/);
    });

    test('should complete interview with lawyers for both parties', async () => {
      // Introduction
      await page.clickContinue();

      // Personal Information
      await page.fillPersonalInfo({
        firstName: 'Alice',
        lastName: 'Johnson'
      });
      await page.clickContinue();

      // Contact Information
      await page.fillContactInfo({
        street: '789 King Street',
        city: 'Ottawa',
        postalCode: 'K1A 0A1',
        phone: '613-555-9999'
      });
      await page.clickContinue();

      // Legal Representation - YES
      await expect(page.page).toHaveText(/Legal Representation/);
      await page.clickYes();
      await page.clickContinue();

      // Lawyer Information
      await expect(page.page).toHaveText(/Your Lawyer's Information/);
      // Fill lawyer details here - need to add fields to the helper
      await page.page.fill('input[name*="user_lawyer"][name*="name.text"]', 'James Wilson');
      await page.page.fill('input[name*="user_lawyer"][name*="lsuc_number"]', 'LSO12345');
      await page.page.fill('input[name*="user_lawyer"][name*="address.address"]', '100 Bay Street');
      await page.page.fill('input[name*="user_lawyer"][name*="address.city"]', 'Toronto');
      await page.page.fill('input[name*="user_lawyer"][name*="address.postal_code"]', 'M5J 2N8');
      await page.page.fill('input[name*="user_lawyer"][name*="phone_number"]', '416-555-0000');
      await page.clickContinue();

      // Other Party's Information
      await page.fillOpposingPartyInfo({
        firstName: 'Bob',
        lastName: 'Williams'
      });
      await page.clickContinue();

      // Other Party has lawyer - YES
      await page.clickYes();
      await page.clickContinue();

      // Other Party's Lawyer
      await expect(page.page).toHaveText(/Other Party's Lawyer Information/);
      await page.page.fill('input[name*="opposing_lawyer"][name*="name.text"]', 'Sarah Lee');
      await page.page.fill('input[name*="opposing_lawyer"][name*="phone_number"]', '416-555-1111');
      await page.clickContinue();

      // Court Information - No file
      await page.fillCourtInfo({
        hasFile: false
      });
      await page.clickContinue();

      // Summary
      await expect(page.page).toHaveText(/Information Collected/);
      await expect(page.page).toHaveText(/Alice Johnson/);
      await expect(page.page).toHaveText(/James Wilson/);
      await expect(page.page).toHaveText(/LSO12345/);
      await expect(page.page).toHaveText(/Bob Williams/);
      await expect(page.page).toHaveText(/Sarah Lee/);
      await expect(page.page).toHaveText(/No existing court file/);
    });
  });

  test.describe('Validation', () => {
    test('should validate required personal information fields', async () => {
      // Skip intro
      await page.clickContinue();

      // Try to continue without filling required fields
      await page.clickContinue();

      // Should show validation errors
      await expect(page.page).toHaveText(/First Name is required/);
      await expect(page.page).toHaveText(/Last Name is required/);
    });

    test('should validate required contact information fields', async () => {
      // Skip intro
      await page.clickContinue();

      // Fill personal info
      await page.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User'
      });
      await page.clickContinue();

      // Try to continue without filling required address fields
      await page.clickContinue();

      // Should show validation errors
      await expect(page.page).toHaveText(/Street Address is required/);
      await expect(page.page).toHaveText(/City is required/);
      await expect(page.page).toHaveText(/Postal Code is required/);
    });

    test('should validate postal code format', async () => {
      await page.clickContinue();

      await page.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User'
      });
      await page.clickContinue();

      // Fill invalid postal code
      await page.fillContactInfo({
        street: '123 Test St',
        city: 'Toronto',
        postalCode: 'INVALID'
      });
      await page.clickContinue();

      // Should show postal code validation error
      await expect(page.page).toHaveText(/valid Canadian postal code/);
    });

    test('should validate email format', async () => {
      await page.clickContinue();

      await page.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User'
      });
      await page.clickContinue();

      await page.fillContactInfo({
        street: '123 Test St',
        city: 'Toronto',
        postalCode: 'M5H 2N2',
        email: 'invalid-email'
      });
      await page.clickContinue();

      // Should show email validation error
      await expect(page.page).toHaveText(/valid email address/);
    });

    test('should validate phone number format', async () => {
      await page.clickContinue();

      await page.fillPersonalInfo({
        firstName: 'Test',
        lastName: 'User'
      });
      await page.clickContinue();

      await page.fillContactInfo({
        street: '123 Test St',
        city: 'Toronto',
        postalCode: 'M5H 2N2',
        phone: '123'  // Too short
      });
      await page.clickContinue();

      // Should show phone validation error
      await expect(page.page).toHaveText(/valid 10 or 11 digit phone number/);
    });
  });

  test.describe('Navigation', () => {
    test('should navigate back through screens', async () => {
      // Go through several screens
      await page.clickContinue(); // Past intro
      
      await page.fillPersonalInfo({
        firstName: 'Nav',
        lastName: 'Test'
      });
      await page.clickContinue(); // To contact info
      
      await page.fillContactInfo({
        street: '123 Test',
        city: 'Toronto',
        postalCode: 'M5H 2N2'
      });
      await page.clickContinue(); // To legal rep

      // Now go back
      await page.clickBack(); // Back to contact
      await expect(page.page).toHaveText(/Your Contact Information/);
      await expect(page.page.locator('input[name*="address.address"]')).toHaveValue('123 Test');

      await page.clickBack(); // Back to personal
      await expect(page.page).toHaveText(/Your Personal Information/);
      await expect(page.page.locator('input[name*="name.first"]')).toHaveValue('Nav');

      await page.clickBack(); // Back to intro
      await expect(page.page).toHaveText(/Ontario Family Law Common Intake/);
    });

    test('should preserve data when navigating back and forth', async () => {
      await page.clickContinue();

      // Fill personal info
      await page.fillPersonalInfo({
        firstName: 'Preserve',
        lastName: 'Data',
        birthdate: '05/20/1975'
      });
      await page.clickContinue();

      // Fill contact info
      await page.fillContactInfo({
        street: '999 Persist Ave',
        city: 'Hamilton',
        postalCode: 'L8P 4Y5',
        email: 'test@example.com'
      });
      
      // Go back to personal info
      await page.clickBack();
      
      // Data should be preserved
      await expect(page.page.locator('input[name*="name.first"]')).toHaveValue('Preserve');
      await expect(page.page.locator('input[name*="birthdate"]')).toHaveValue('05/20/1975');
      
      // Go forward again
      await page.clickContinue();
      
      // Contact data should also be preserved
      await expect(page.page.locator('input[name*="address.city"]')).toHaveValue('Hamilton');
      await expect(page.page.locator('input[name*="email"]')).toHaveValue('test@example.com');
    });
  });
});