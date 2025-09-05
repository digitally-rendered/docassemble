import { test, expect, Page } from '@playwright/test';

/**
 * Comprehensive Playwright tests for ALL flows in Ontario Family Law Common Intake Enhanced Interview
 * 
 * This test suite covers all possible paths through the interview:
 * 1. Emergency vs Non-emergency
 * 2. MIP Status variations (completed, not completed, unsure, emergency defer)
 * 3. Different relationship statuses
 * 4. Various order combinations (triggering financial forms)
 * 5. With/without lawyers
 * 6. With/without existing court file
 * 7. With/without children
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
  minorUser: {
    firstName: 'Jane',
    lastName: 'Minor',
    birthDate: new Date(new Date().setFullYear(new Date().getFullYear() - 10)).toISOString().split('T')[0] // 10 years old
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
  opposingLawyer: {
    name: 'Robert Brown',
    firm: 'Brown Legal',
    lsoNumber: '54321B',
    streetAddress: '100 King Street',
    suite: 'Suite 800',
    city: 'Toronto',
    province: 'Ontario',
    postalCode: 'M5X 1E2',
    phoneNumber: '4165553000',
    extension: '456',
    faxNumber: '4165553001',
    email: 'rbrown@brownlegal.com'
  },
  validCourt: {
    name: 'Superior Court of Justice',
    location: 'Toronto',
    fileNumber: 'FC-24-123456'
  },
  childInfo: {
    firstName: 'Emma',
    lastName: 'Smith',
    birthDate: '2015-03-15',
    livesWiths: 'Both (shared)'
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
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
    await this.clickContinue();
  }

  async handleEmergencyCheck(isEmergency: boolean = false) {
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
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Mandatory Information Program (MIP) Status');
    
    const buttonText = {
      'completed': 'Yes, I have my certificate',
      'not_completed': 'No, I need to attend',
      'unsure': 'Not sure',
      'emergency_defer': 'Emergency - will complete after'
    };
    
    await this.clickButton(buttonText[status]);
    
    // Handle MIP information screen if needed
    // Based on the interview YAML line 28, only "not_completed" shows the MIP info screen
    if (status === 'not_completed') {
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
    
    // Simply click on the text label which should toggle the checkbox
    for (const order of orders) {
      // Some orders may not be visible depending on relationship status
      const orderElement = this.page.getByText(order, { exact: false }).first();
      const isVisible = await orderElement.isVisible().catch(() => false);
      if (isVisible) {
        await orderElement.click();
      }
    }
    
    await this.clickContinue();
  }

  async handleFinancialSituation(options: any = {}) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Financial Information');
    
    // Fill in financial info based on options using radio buttons
    // Click on the label text or the radio element itself
    if (options.claimingSupport) {
      await this.page.getByRole('radio', { name: 'Yes' }).first().click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).first().click();
    }
    
    if (options.payingSupport) {
      await this.page.getByRole('radio', { name: 'Yes' }).nth(1).click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).nth(1).click();
    }
    
    if (options.ownsRealEstate) {
      await this.page.getByRole('radio', { name: 'Yes' }).nth(2).click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).nth(2).click();
    }
    
    if (options.ownsBusiness) {
      await this.page.getByRole('radio', { name: 'Yes' }).nth(3).click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).nth(3).click();
    }
    
    if (options.hasInvestments) {
      await this.page.getByRole('radio', { name: 'Yes' }).nth(4).click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).nth(4).click();
    }
    
    if (options.hasPension) {
      await this.page.getByRole('radio', { name: 'Yes' }).nth(5).click();
    } else {
      await this.page.getByRole('radio', { name: 'No' }).nth(5).click();
    }
    
    if (options.totalAssets !== undefined) {
      // Use getByLabel to find the field more reliably
      await this.page.getByLabel('Total value of assets').fill(options.totalAssets.toString());
    }
    if (options.totalDebts !== undefined) {
      // Use getByLabel to find the field more reliably
      await this.page.getByLabel('Total debts').fill(options.totalDebts.toString());
    }
    
    await this.clickContinue();
  }

  async fillPersonalInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Your Personal Information');
    
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
      const radioLabel = data.contactPreference === 'phone' ? 'Phone' : data.contactPreference === 'email' ? 'Email' : 'Mail';
      await this.page.getByRole('radio', { name: radioLabel }).click();
    }
    
    await this.clickContinue();
  }

  async handleLegalRepresentation(hasLawyer: boolean = false) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Do you have a lawyer?');
    
    if (hasLawyer) {
      await this.clickButton('Yes');
    } else {
      await this.clickButton('No');
    }
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
      // When yes, we'll need to fill in lawyer info
    } else if (hasLawyer === 'unknown') {
      await this.clickButton('Unknown');
      // When unknown, interview still shows optional lawyer info screens
      await this.clickContinue(); // Skip optional lawyer info
      await this.clickContinue(); // Skip optional lawyer contact
    } else {
      await this.clickButton('No');
      // When no, interview still shows optional lawyer info screens
      await this.clickContinue(); // Skip optional lawyer info
      await this.clickContinue(); // Skip optional lawyer contact
    }
  }

  async fillOpposingLawyerInfo(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Other Party Lawyer Information');
    
    if (data.name) {
      await this.page.getByLabel('Lawyer Name', { exact: false }).fill(data.name);
    }
    if (data.firm) {
      await this.page.getByLabel('Law Firm', { exact: false }).fill(data.firm);
    }
    if (data.lsoNumber) {
      await this.page.getByLabel('Law Society Number', { exact: false }).fill(data.lsoNumber);
    }
    
    await this.clickContinue();
  }

  async fillOpposingLawyerContact(data: any) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Other Party Lawyer Contact Information');
    
    if (data.streetAddress) {
      await this.page.getByLabel('Street Address', { exact: false }).fill(data.streetAddress);
    }
    if (data.suite) {
      await this.page.getByLabel('Suite/Unit', { exact: false }).fill(data.suite);
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
      await this.page.getByLabel('Phone', { exact: false }).fill(data.phoneNumber);
    }
    // Note: Extension field is not present for opposing lawyer
    if (data.faxNumber) {
      await this.page.getByLabel('Fax', { exact: false }).fill(data.faxNumber);
    }
    if (data.email) {
      await this.page.getByLabel('Email', { exact: false }).fill(data.email);
    }
    
    await this.clickContinue();
  }

  async handleCourtInfo(hasExistingFile: boolean = false, data: any = null) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Court Information');
    
    if (hasExistingFile) {
      await this.page.getByRole('radio', { name: 'Yes' }).click();
      
      // Wait for conditional fields
      await this.page.waitForTimeout(500);
      
      if (data) {
        await this.page.getByLabel('Court Name', { exact: false }).selectOption(data.name);
        await this.page.getByLabel('Court Location', { exact: false }).fill(data.location);
        await this.page.getByLabel('Court File Number', { exact: false }).fill(data.fileNumber);
      }
    } else {
      await this.page.getByRole('radio', { name: 'No' }).click();
    }
    
    await this.clickContinue();
  }

  async handleChildren(hasChildren: boolean = false, numChildren: number = 0) {
    await expect(this.page.locator('h1#daMainQuestion')).toContainText('Do you have children together?');
    
    if (hasChildren) {
      await this.clickButton('Yes');
      
      // Specify number of children - the actual heading is "Children Information"
      await expect(this.page.locator('h1#daMainQuestion')).toContainText('Children Information');
      await this.page.getByLabel('How many children?', { exact: false }).fill(numChildren.toString());
      await this.clickContinue();
      
      // Fill info for each child
      for (let i = 0; i < numChildren; i++) {
        await expect(this.page.locator('h1#daMainQuestion')).toContainText(`Information for Child`);
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

  async verifySummaryContains(text: string) {
    await expect(this.page.locator('body')).toContainText(text);
  }
}

// Test Suite
test.describe('Enhanced Common Intake - All Flows', () => {
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

  // Test 1: Emergency flow with restraining order
  test('emergency flow with restraining order and MIP defer', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(true); // Emergency
    await intake.handleMIPStatus('emergency_defer'); // Will complete MIP after
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Restraining order', 'Child custody and/or access']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.handleCourtInfo(false);
    await intake.handleChildren(false);
    await intake.expectSummaryScreen();
    
    // Verify emergency status and forms
    await intake.verifySummaryContains('Emergency: Yes - URGENT');
    await intake.verifySummaryContains('Form 14B - Motion');
    await intake.verifySummaryContains('Form 25F - Restraining Order');
  });

  // Test 2: Common-law with financial forms
  test('common-law relationship with property division and support', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('common_law');
    await intake.handleOrdersSought(['Child support', 'Spousal support', 'Property division/equalization']);
    
    // Financial situation screen should appear
    await intake.handleFinancialSituation({
      claimingSupport: true,
      payingSupport: false,
      ownsRealEstate: true,
      ownsBusiness: false,
      hasInvestments: true,
      hasPension: true,
      totalAssets: 500000,
      totalDebts: 100000
    });
    
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(true);
    await intake.fillLawyerInfo(TEST_DATA.validLawyer);
    await intake.fillLawyerContact(TEST_DATA.validLawyer);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(true);
    await intake.fillOpposingLawyerInfo(TEST_DATA.opposingLawyer);
    await intake.fillOpposingLawyerContact(TEST_DATA.opposingLawyer);
    await intake.handleCourtInfo(true, TEST_DATA.validCourt);
    await intake.handleChildren(true, 2); // 2 children
    await intake.expectSummaryScreen();
    
    // Verify financial forms are recommended
    await intake.verifySummaryContains('Financial Information');
    await intake.verifySummaryContains('Form 13 - Financial Statement (Support)');
    await intake.verifySummaryContains('Form 13.1 - Financial Statement (Property)');
  });

  // Test 3: Never together with paternity
  test('never together seeking paternity and child support', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('not_completed'); // Needs to attend MIP
    await intake.handleRelationshipStatus('never_together');
    
    // For never_together, certain options like spousal support shouldn't be available
    await intake.handleOrdersSought(['Child support', 'Child custody and/or access']);
    
    await intake.handleFinancialSituation({
      claimingSupport: true,
      payingSupport: false,
      ownsRealEstate: false,
      ownsBusiness: false,
      hasInvestments: false,
      hasPension: false
    });
    
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep('unknown'); // Unknown if they have a lawyer
    await intake.handleCourtInfo(false); // No existing file
    await intake.handleChildren(true, 1); // 1 child
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('MIP Status: Not Completed');
    await intake.verifySummaryContains('Relationship: Never Together');
  });

  // Test 4: Divorced seeking variation
  test('divorced seeking variation of existing order', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('divorced');
    await intake.handleOrdersSought(['Variation of existing order']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.handleCourtInfo(true, TEST_DATA.validCourt); // Has existing file
    await intake.handleChildren(false);
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('Relationship: Divorced');
    await intake.verifySummaryContains('Variation');
    await intake.verifySummaryContains('Court: Superior Court of Justice');
  });

  // Test 5: Separated with full representation
  test('separated with both parties having lawyers', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('separated');
    await intake.handleOrdersSought(['Child custody and/or access', 'Child support', 'Spousal support']);
    
    await intake.handleFinancialSituation({
      claimingSupport: false,
      payingSupport: true,
      ownsRealEstate: true,
      ownsBusiness: true,
      hasInvestments: true,
      hasPension: true
    });
    
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(true);
    await intake.fillLawyerInfo(TEST_DATA.validLawyer);
    await intake.fillLawyerContact(TEST_DATA.validLawyer);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(true);
    await intake.fillOpposingLawyerInfo(TEST_DATA.opposingLawyer);
    await intake.fillOpposingLawyerContact(TEST_DATA.opposingLawyer);
    await intake.handleCourtInfo(true, TEST_DATA.validCourt);
    await intake.handleChildren(true, 3); // 3 children
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('Sarah Johnson');
    await intake.verifySummaryContains('Robert Brown');
    await intake.verifySummaryContains('Number of Children: 3');
  });

  // Test 6: MIP unsure status
  test('MIP unsure status flow', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('unsure'); // Not sure about MIP
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Child custody and/or access']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.handleCourtInfo(false);
    await intake.handleChildren(false);
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('MIP Status: Unsure');
  });

  // Test 7: Dating relationship
  test('dating but not living together', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('dating');
    await intake.handleOrdersSought(['Child custody and/or access', 'Child support']);
    
    await intake.handleFinancialSituation({
      claimingSupport: false,
      payingSupport: false,
      ownsRealEstate: false,
      ownsBusiness: false,
      hasInvestments: false,
      hasPension: false
    });
    
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.handleCourtInfo(false);
    await intake.handleChildren(true, 1);
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('Relationship: Dating But Not Living Together');
  });

  // Test 8: Enforcement of existing order
  test('seeking enforcement of existing order', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('divorced');
    await intake.handleOrdersSought(['Enforcement of existing order']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(false);
    await intake.fillOpposingPartyInfo(TEST_DATA.validOpposingParty);
    await intake.fillOpposingPartyContact(TEST_DATA.validOpposingParty);
    await intake.handleOpposingLegalRep(false);
    await intake.handleCourtInfo(true, TEST_DATA.validCourt); // Should have existing order
    await intake.handleChildren(false);
    await intake.expectSummaryScreen();
    
    await intake.verifySummaryContains('Enforcement');
    await intake.verifySummaryContains('File #: FC-24-123456');
  });

  // Test 9: Validation tests
  test('postal code validation', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Child custody and/or access']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    
    // Try invalid postal code
    await page.getByLabel('Street Address', { exact: false }).fill('123 Main St');
    await page.getByLabel('City', { exact: false }).fill('Toronto');
    await page.getByLabel('Province', { exact: false }).selectOption('Ontario');
    await page.getByLabel('Postal Code', { exact: false }).fill('INVALID');
    await page.getByLabel('Phone Number', { exact: false }).fill('4165551234');
    
    await intake.clickContinue();
    
    // Should show validation error
    const errorElement = await page.locator('.da-has-error, .text-danger, .da-field-error').first();
    await expect(errorElement).toBeVisible();
    
    // Fix postal code
    await page.getByLabel('Postal Code', { exact: false }).fill('M5V 3A8');
    await intake.clickContinue();
    
    // Should proceed
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have a lawyer?');
  });

  // Test 10: LSO number validation
  test('lawyer LSO number validation', async () => {
    await intake.handleIntroduction();
    await intake.handleEmergencyCheck(false);
    await intake.handleMIPStatus('completed');
    await intake.handleRelationshipStatus('married');
    await intake.handleOrdersSought(['Child custody and/or access']);
    await intake.fillPersonalInfo(TEST_DATA.validUser);
    await intake.fillContactInfo(TEST_DATA.validUser);
    await intake.handleLegalRepresentation(true);
    
    // Try invalid LSO number
    await page.getByLabel('Lawyer Name', { exact: false }).fill('Test Lawyer');
    await page.getByLabel('Law Society Number', { exact: false }).fill('INVALID');
    
    await intake.clickContinue();
    
    // Should show validation error
    await expect(page.locator('h1#daMainQuestion')).toContainText('Your Lawyer Information');
    
    // Fix LSO number
    await page.getByLabel('Law Society Number', { exact: false }).clear();
    await page.getByLabel('Law Society Number', { exact: false }).fill('12345A');
    await intake.clickContinue();
    
    // Should proceed to lawyer contact info
    await expect(page.locator('h1#daMainQuestion')).toContainText('Your Lawyer Contact Information');
  });
});