import { test, expect, Page } from '@playwright/test';

/**
 * Fixed Playwright tests for Ontario Family Law Common Intake Enhanced Interview
 * This version correctly handles the actual flow which includes:
 * 1. Introduction
 * 2. Emergency check
 * 3. MIP status check
 * 4. Relationship status
 * 5. Orders being sought
 * 6. Financial situation (if applicable)
 * 7. Personal information
 * 8. Contact information
 * 9. Legal representation
 * 10. Other party information
 * 11. Court information
 * 12. Children information (if applicable)
 * 13. Summary
 */

// Test configuration  
const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';
const DEFAULT_TIMEOUT = 30000;

// Test data constants
const TEST_DATA = {
  validUser: {
    firstName: 'John',
    middleName: 'Michael',
    lastName: 'Smith',
    alsoKnownAs: 'Johnny, J. Smith',
    birthDate: '1980-01-15',
    streetAddress: '123 Main Street',
    unit: 'Apt 5',
    city: 'Toronto',
    province: 'Ontario',
    postalCode: 'M5V 3A8',
    phoneNumber: '4165551234',
    alternativePhone: '6475559876',
    email: 'john.smith@example.com',
    contactPreference: 'email'
  },
  validOpposingParty: {
    firstName: 'Jane',
    middleName: 'Marie',
    lastName: 'Doe',
    birthDate: '1985-06-20',
    streetAddress: '456 Oak Avenue',
    city: 'Mississauga',
    province: 'Ontario',
    postalCode: 'L5B 4L8',
    phoneNumber: '9055551234',
    email: 'jane.doe@example.com'
  },
  validLawyer: {
    name: 'Sarah Johnson',
    firm: 'Johnson & Associates',
    lsoNumber: '12345A',
    streetAddress: '200 Bay Street',
    suite: 'Suite 1500',
    city: 'Toronto',
    province: 'Ontario',
    postalCode: 'M5J 2J2',
    phoneNumber: '4165552000',
    extension: '123',
    faxNumber: '4165552001',
    email: 'sjohnson@lawfirm.com'
  },
  validCourt: {
    name: 'Superior Court of Justice',
    location: 'Toronto',
    fileNumber: 'FC-24-123456'
  }
};

// Helper class for common intake page interactions
class EnhancedIntakePage {
  constructor(private page: Page) {}

  // Navigation helpers
  async navigateToInterview() {
    await this.page.goto(INTERVIEW_URL);
    await this.page.waitForLoadState('networkidle');
  }

  async clickContinue() {
    // Look for various continue button selectors
    const continueButton = this.page.locator('button:has-text("Continue")').first();
    await continueButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async clickButton(text: string) {
    await this.page.click(`button:has-text("${text}")`);
    await this.page.waitForLoadState('networkidle');
  }

  // Screen flow handlers
  async handleIntroduction() {
    // Check we're on intro screen
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
    await this.clickContinue();
  }

  async handleEmergencyCheck(isEmergency: boolean = false) {
    // Check we're on emergency screen
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Is this an emergency situation?');
    
    if (isEmergency) {
      await this.clickButton('Yes, this is an emergency');
      // Handle emergency warning screen
      await expect(this.page.locator('h1#daMainQuestion')).toContainText('URGENT: Emergency Filing Required');
      await this.clickButton('Continue (I understand the urgency)');
    } else {
      await this.clickButton('No, this is not an emergency');
    }
  }

  async handleMIPStatus(status: 'completed' | 'not_completed' | 'unsure' | 'emergency_defer' = 'completed') {
    // Check we're on MIP status screen
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Mandatory Information Program (MIP) Status');
    
    const buttonText = {
      'completed': 'Yes, I have my certificate',
      'not_completed': 'No, I need to attend',
      'unsure': 'Not sure',
      'emergency_defer': 'Emergency - will complete after'
    };
    
    await this.clickButton(buttonText[status]);
    
    // Handle MIP information screen if needed
    if (status === 'not_completed' || status === 'unsure' || status === 'emergency_defer') {
      await expect(this.page.locator('h1#daMainQuestion')).toContainText('MIP Registration Required');
      await this.clickContinue();
    }
  }

  async handleRelationshipStatus(status: string = 'married') {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('What is your relationship status');
    
    const statusMap = {
      'married': 'Married',
      'common_law': 'Common-law partners',
      'never_together': 'Never lived together',
      'dating': 'Dating but not living together',
      'separated': 'Separated',
      'divorced': 'Divorced'
    };
    
    await this.clickButton(statusMap[status] || status);
  }

  async handleOrdersSought(orders: string[] = []) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('What orders are you seeking?');
    
    // Map order names to field names
    const orderFieldMap = {
      'Divorce': 'seeking_divorce',
      'Child custody and/or access': 'seeking_custody',
      'Child support': 'seeking_child_support',
      'Spousal support': 'seeking_spousal_support',
      'Property division/equalization': 'seeking_property',
      'Exclusive possession of home': 'seeking_exclusive_possession',
      'Restraining order': 'seeking_restraining_order',
      'Paternity/parentage declaration': 'seeking_paternity',
      'Enforcement of existing order': 'seeking_enforcement',
      'Variation of existing order': 'seeking_variation',
      'Other relief': 'seeking_other'
    };
    
    // Check the appropriate checkboxes - they appear to be rendered as individual checkboxes, not a group
    for (const order of orders) {
      // Simply click on the text label which should toggle the checkbox
      await this.page.getByText(order, { exact: false }).first().click();
    }
    
    await this.clickContinue();
  }

  async handleFinancialSituation() {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Financial Information');
    
    // Fill in basic financial info
    await this.page.click('input[name="claiming_support"][value="False"]');
    await this.page.click('input[name="paying_support"][value="False"]');
    await this.page.click('input[name="owns_real_estate"][value="False"]');
    await this.page.click('input[name="owns_business"][value="False"]');
    await this.page.click('input[name="has_investments"][value="False"]');
    await this.page.click('input[name="has_pension"][value="False"]');
    
    await this.clickContinue();
  }

  async fillPersonalInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Your Personal Information');
    
    // Use getByLabel to find fields by their label text
    await this.page.getByLabel('First Name', { exact: false }).fill(data.firstName);
    if (data.middleName) {
      await this.page.getByLabel('Middle Name', { exact: false }).fill(data.middleName);
    }
    await this.page.getByLabel('Last Name', { exact: false }).fill(data.lastName);
    if (data.birthDate) {
      await this.page.getByLabel('Date of Birth', { exact: false }).fill(data.birthDate);
    }
    if (data.alsoKnownAs) {
      await this.page.getByLabel('Also known as', { exact: false }).fill(data.alsoKnownAs);
    }
    
    await this.clickContinue();
  }

  async fillContactInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Your Contact Information');
    
    await this.page.getByLabel('Street Address', { exact: false }).fill(data.streetAddress);
    if (data.unit) {
      await this.page.getByLabel('Unit/Apt', { exact: false }).fill(data.unit);
    }
    await this.page.getByLabel('City', { exact: false }).fill(data.city);
    await this.page.getByLabel('Province', { exact: false }).selectOption(data.province);
    await this.page.getByLabel('Postal Code', { exact: false }).fill(data.postalCode);
    await this.page.getByLabel('Phone Number', { exact: false }).fill(data.phoneNumber);
    if (data.alternativePhone) {
      await this.page.getByLabel('Alternative Phone', { exact: false }).fill(data.alternativePhone);
    }
    if (data.email) {
      await this.page.getByLabel('Email Address', { exact: false }).fill(data.email);
    }
    if (data.contactPreference) {
      // Use getByRole for radio buttons to be more specific
      const radioLabel = data.contactPreference === 'phone' ? 'Phone' : data.contactPreference === 'email' ? 'Email' : 'Mail';
      await this.page.getByRole('radio', { name: radioLabel }).click();
    }
    
    await this.clickContinue();
  }

  async handleLegalRepresentation(hasLawyer: boolean = false) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Do you have a lawyer?');
    
    // These are button elements, not radio buttons
    if (hasLawyer) {
      await this.clickButton('Yes');
    } else {
      await this.clickButton('No');
    }
    // No need to click continue as buttons auto-submit
  }

  async fillLawyerInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Your Lawyer Information');
    
    await this.page.getByLabel('Lawyer Name', { exact: false }).fill(data.name);
    if (data.firm) {
      await this.page.getByLabel('Law Firm', { exact: false }).fill(data.firm);
    }
    await this.page.getByLabel('Law Society Number', { exact: false }).fill(data.lsoNumber);
    
    await this.clickContinue();
  }

  async fillLawyerContact(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Your Lawyer Contact Information');
    
    await this.page.getByLabel('Street Address', { exact: false }).fill(data.streetAddress);
    if (data.suite) {
      await this.page.getByLabel('Suite/Unit', { exact: false }).fill(data.suite);
    }
    await this.page.getByLabel('City', { exact: false }).fill(data.city);
    await this.page.getByLabel('Province', { exact: false }).selectOption(data.province);
    await this.page.getByLabel('Postal Code', { exact: false }).fill(data.postalCode);
    await this.page.getByLabel('Phone', { exact: false }).first().fill(data.phoneNumber);
    if (data.extension) {
      await this.page.getByLabel('Extension', { exact: false }).fill(data.extension);
    }
    if (data.faxNumber) {
      await this.page.getByLabel('Fax', { exact: false }).fill(data.faxNumber);
    }
    if (data.email) {
      await this.page.getByLabel('Email', { exact: false }).fill(data.email);
    }
    
    await this.clickContinue();
  }

  async fillOpposingPartyInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Other Party Information');
    
    await this.page.getByLabel('First Name', { exact: false }).fill(data.firstName);
    if (data.middleName) {
      await this.page.getByLabel('Middle Name', { exact: false }).fill(data.middleName);
    }
    await this.page.getByLabel('Last Name', { exact: false }).fill(data.lastName);
    if (data.birthDate) {
      await this.page.getByLabel('Date of Birth', { exact: false }).fill(data.birthDate);
    }
    
    await this.clickContinue();
  }

  async fillOpposingPartyContact(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Other Party Contact Information');
    
    if (data.streetAddress) {
      await this.page.getByLabel('Street Address', { exact: false }).fill(data.streetAddress);
    }
    if (data.city) {
      await this.page.getByLabel('City', { exact: false }).fill(data.city);
    }
    if (data.province) {
      await this.page.getByLabel('Province', { exact: false }).selectOption(data.province);
    }
    if (data.postalCode) {
      await this.page.getByLabel('Postal Code', { exact: false }).fill(data.postalCode);
    }
    if (data.phoneNumber) {
      await this.page.getByLabel('Phone Number', { exact: false }).fill(data.phoneNumber);
    }
    if (data.email) {
      await this.page.getByLabel('Email', { exact: false }).fill(data.email);
    }
    
    await this.clickContinue();
  }

  async handleOpposingLegalRep(hasLawyer: boolean | 'unknown' = false) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Does the other party have a lawyer?');
    
    if (hasLawyer === true) {
      await this.clickButton('Yes');
    } else if (hasLawyer === 'unknown') {
      await this.clickButton('Unknown');
    } else {
      await this.clickButton('No');
    }
    // No need to click continue as buttons auto-submit
  }

  async fillCourtInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Court Information');
    
    // Say yes to existing court file - click on the radio button's label text
    await this.page.getByRole('radio', { name: 'Yes' }).click();
    
    // Wait a moment for conditional fields to appear
    await this.page.waitForTimeout(500);
    
    // Fill court details on the same screen (they appear conditionally)
    await this.page.getByLabel('Court Name', { exact: false }).selectOption(data.name);
    await this.page.getByLabel('Court Location', { exact: false }).fill(data.location);
    await this.page.getByLabel('Court File Number', { exact: false }).fill(data.fileNumber);
    
    await this.clickContinue();
  }

  async handleChildren(hasChildren: boolean = false, numChildren: number = 0) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Do you have children together?');
    
    if (hasChildren) {
      await this.clickButton('Yes');
      
      // Specify number of children
      await expect(this.page.locator('h1#daMainQuestion')).toContainText('Children Information');
      await this.page.getByLabel('How many children?', { exact: false }).fill(numChildren.toString());
      await this.clickContinue();
      
      // Fill info for each child
      for (let i = 0; i < numChildren; i++) {
        await expect(this.page.locator('h1#daMainQuestion')).toContainText(`Information for Child ${i + 1}`);
        await this.page.getByLabel('First Name', { exact: false }).fill(`Child${i + 1}`);
        await this.page.getByLabel('Last Name', { exact: false }).fill('Smith');
        await this.page.getByLabel('Date of Birth', { exact: false }).fill('2015-01-01');
        await this.page.getByLabel('Lives with', { exact: false }).selectOption('Both (shared)');
        await this.clickContinue();
      }
    } else {
      await this.clickButton('No');
    }
  }

  async expectSummaryScreen() {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Information Summary');
  }

  // Validation helpers
  async expectValidationError(fieldName: string, errorMessage?: string) {
    const errorSelector = `.da-has-error:has(input[name="${fieldName}"]) .help-block, .text-danger, .da-field-error`;
    const errorElement = await this.page.locator(errorSelector).first();
    
    if (errorMessage) {
      await expect(errorElement).toContainText(errorMessage);
    } else {
      await expect(errorElement).toBeVisible();
    }
  }
}

// Test Suite
test.describe('Enhanced Common Intake - Complete Flow', () => {
  let page: Page;
  let intake: EnhancedIntakePage;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    intake = new EnhancedIntakePage(page);
    await intake.navigateToInterview();
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('should complete non-emergency flow with no lawyer', async () => {
    // Introduction
    await intake.handleIntroduction();
    
    // Emergency check - No
    await intake.handleEmergencyCheck(false);
    
    // MIP Status - Completed
    await intake.handleMIPStatus('completed');
    
    // Relationship status
    await intake.handleRelationshipStatus('married');
    
    // Orders sought - select child custody which should be visible for all relationships
    await intake.handleOrdersSought(['Child custody and/or access']);
    
    // Personal info
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    
    // Contact info with validation
    await intake.fillContactInfo(TEST_DATA.validUser);
    
    // Legal representation - No
    await intake.handleLegalRepresentation(false);
    
    // Opposing party info
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    
    // Opposing party contact
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    
    // Opposing party lawyer - No
    await intake.handleOpposingLegalRep(false);
    
    // Even when opposing party has no lawyer, the interview shows a screen for optional lawyer info
    // We'll just continue through it
    await intake.clickContinue();  // Skip opposing lawyer info
    await intake.clickContinue();  // Skip opposing lawyer contact
    
    // Court info
    await intake.fillCourtInfo(TEST_DATA.validCourt);
    
    // Children - No
    await intake.handleChildren(false);
    
    // Should reach summary
    await intake.expectSummaryScreen();
    
    // Verify key data is displayed (name is abbreviated to M. for middle name)
    await expect(page.locator('body')).toContainText('John M. Smith');
    await expect(page.locator('body')).toContainText('M5V 3A8');
    await expect(page.locator('body')).toContainText('FC-24-123456');
  });

  test('should complete emergency flow with lawyers', async () => {
    // Introduction
    await intake.handleIntroduction();
    
    // Emergency check - Yes
    await intake.handleEmergencyCheck(true);
    
    // MIP Status - Emergency defer
    await intake.handleMIPStatus('emergency_defer');
    
    // Relationship status
    await intake.handleRelationshipStatus('married');
    
    // Orders sought - multiple including restraining order
    await intake.handleOrdersSought(['Divorce', 'Restraining order', 'Child custody and/or access']);
    
    // Personal info
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    
    // Contact info
    await intake.fillContactInfo(TEST_DATA.validUser);
    
    // Legal representation - Yes
    await intake.handleLegalRepresentation(true);
    
    // Lawyer info
    await intake.fillLawyerInfo(TEST_DATA.validLawyer);
    await intake.fillLawyerContact(TEST_DATA.validLawyer);
    
    // Opposing party info
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    
    // Opposing party lawyer - Yes
    await intake.handleOpposingLegalRep(true);
    
    // We can skip opposing lawyer details (optional fields)
    await intake.clickContinue();
    await intake.clickContinue();
    
    // Court info
    await intake.fillCourtInfo(TEST_DATA.validCourt);
    
    // Children - Yes with 2 children
    await intake.handleChildren(true, 2);
    
    // Should reach summary
    await intake.expectSummaryScreen();
    
    // Verify emergency status
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('Sarah Johnson');
  });

  test('should handle financial forms flow', async () => {
    // Introduction
    await intake.handleIntroduction();
    
    // Emergency check - No
    await intake.handleEmergencyCheck(false);
    
    // MIP Status - Completed
    await intake.handleMIPStatus('completed');
    
    // Relationship status
    await intake.handleRelationshipStatus('married');
    
    // Orders sought - triggers financial forms
    await intake.handleOrdersSought(['Child support', 'Spousal support', 'Property division/equalization']);
    
    // Financial situation screen should appear
    await intake.handleFinancialSituation();
    
    // Continue with rest of flow
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.fillCourtInfo(TEST_DATA.validCourt);
    await intake.handleChildren(false);
    
    // Should reach summary
    await intake.expectSummaryScreen();
    
    // Verify financial info section appears
    await expect(page.locator('body')).toContainText('Financial Information');
  });

  test('should validate postal code format', async () => {
    // Navigate to contact info screen
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Divorce']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    
    // Try invalid postal code
    await page.fill('input[name="user.address.address"]', '123 Main St');
    await page.fill('input[name="user.address.city"]', 'Toronto');
    await page.selectOption('select[name="user.address.state"]', 'Ontario');
    await page.fill('input[name="user.address.postal_code"]', 'INVALID');
    await page.fill('input[name="user.phone_number"]', '4165551234');
    
    await intake.clickContinue();
    
    // Should show validation error
    await intake.expectValidationError('user.address.postal_code', 'valid Canadian postal code');
    
    // Fix postal code
    await page.fill('input[name="user.address.postal_code"]', 'M5V 3A8');
    await intake.clickContinue();
    
    // Should proceed
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have a lawyer?');
  });

  test('should validate LSO number format', async () => {
    // Navigate to lawyer info screen
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Divorce']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(true);
    
    // Try invalid LSO number
    await page.fill('input[name="user_lawyer.name.text"]', 'Test Lawyer');
    await page.fill('input[name="user_lawyer.lsuc_number"]', 'INVALID');
    
    await intake.clickContinue();
    
    // Should show validation error
    await intake.expectValidationError('user_lawyer.lsuc_number', '5 digits, optionally followed by a letter');
    
    // Fix LSO number
    await page.fill('input[name="user_lawyer.lsuc_number"]', '12345A');
    await intake.clickContinue();
    
    // Should proceed to lawyer contact info
    await expect(page.locator('h1#daMainQuestion')).toContainText('Your Lawyer Contact Information');
  });

  test('should handle date validation', async () => {
    // Navigate to personal info
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Divorce']);
    
    // Test with minor (10 years old)
    const minorDate = new Date();
    minorDate.setFullYear(minorDate.getFullYear() - 10);
    
    await page.fill('input[name="user.name.first"]', 'Test');
    await page.fill('input[name="user.name.last"]', 'Minor');
    await page.fill('input[name="user.birthdate"]', minorDate.toISOString().split('T')[0]);
    
    await intake.clickContinue();
    
    // Should proceed but might show a note about being under 18
    await expect(page.locator('h1#daMainQuestion')).toContainText('Your Contact Information');
  });
});