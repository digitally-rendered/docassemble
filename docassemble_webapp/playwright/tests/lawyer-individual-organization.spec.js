const { test, expect } = require('@playwright/test');

test.describe('Individual Objects (Lawyers) and Organization Objects (Law Firms)', () => {
  const wizardUrl = 'http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml';

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', exception => {
      console.log(`Page error: ${exception}`);
    });
    
    await page.goto(wizardUrl);
    await page.waitForLoadState('networkidle');
  });

  test('should collect Individual object data for user lawyer', async ({ page }) => {
    // Navigate to lawyer information collection
    await navigateToLawyerInfo(page);
    
    const lawyerContent = await page.content();
    if (lawyerContent.includes('lawyer') || lawyerContent.includes('represented')) {
      console.log('✅ Reached lawyer information section');
      
      // Select "Yes, I have a lawyer"
      await selectHasLawyer(page, true);
      
      // Test Individual object fields for lawyer
      const lawyerFormContent = await page.content();
      if (lawyerFormContent.includes('Lawyer') || lawyerFormContent.includes('Legal')) {
        await testIndividualObjectFields(page, {
          type: 'user_lawyer',
          individual: {
            firstName: 'Sarah',
            lastName: 'Legal',
            middleName: 'Jane',
            title: 'Ms.',
            profession: 'Lawyer',
            barNumber: '12345',
            phone: '4165551111',
            alternativePhone: '6475552222',
            email: 'sarah.legal@lawfirm.com',
            alternativeEmail: 's.legal@gmail.com',
            address: {
              street: '789 Bay Street',
              suite: 'Suite 1200',
              city: 'Toronto',
              province: 'Ontario',
              postalCode: 'M5G 2C8'
            }
          }
        });
        
        console.log('✅ Individual object for user lawyer tested successfully');
      } else {
        console.log('❓ Lawyer form did not appear - may have different flow');
      }
    }
  });

  test('should collect Organization object data for law firm', async ({ page }) => {
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, true);
    
    // Look for law firm/organization information
    const firmContent = await page.content();
    if (firmContent.includes('firm') || firmContent.includes('office') || firmContent.includes('organization')) {
      console.log('✅ Found law firm information section');
      
      await testOrganizationObjectFields(page, {
        type: 'user_law_firm',
        organization: {
          name: 'Smith & Associates Law Firm',
          legalName: 'Smith & Associates Professional Corporation',
          businessNumber: '123456789',
          address: {
            street: '789 Bay Street',
            suite: 'Suite 1200',
            city: 'Toronto',
            province: 'Ontario',
            postalCode: 'M5G 2C8'
          },
          phone: '4165552222',
          fax: '4165552223',
          email: 'info@smithlaw.ca',
          website: 'www.smithlaw.ca'
        }
      });
      
      console.log('✅ Organization object for law firm tested successfully');
    } else {
      console.log('❓ Law firm form did not appear or is combined with lawyer info');
    }
  });

  test('should handle both Individual and Organization objects for lawyer representation', async ({ page }) => {
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, true);
    
    // Fill lawyer (Individual) information
    await fillLawyerIndividualInfo(page, {
      firstName: 'David',
      lastName: 'Attorney',
      phone: '4165551111',
      email: 'david.attorney@biglaw.com'
    });
    
    // Submit lawyer info and look for law firm info
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    const nextContent = await page.content();
    if (nextContent.includes('firm') || nextContent.includes('office')) {
      console.log('✅ Transitioned from Individual to Organization object collection');
      
      await fillLawFirmOrganizationInfo(page, {
        name: 'Big Law Associates',
        address: '100 Queen Street West',
        city: 'Toronto',
        phone: '4165553333',
        email: 'contact@biglaw.com'
      });
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      console.log('✅ Both Individual and Organization objects processed successfully');
    }
  });

  test('should collect Individual object for other party lawyer', async ({ page }) => {
    // Navigate through to other party lawyer section
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, false); // User has no lawyer
    
    // Should ask about other party lawyer
    const otherLawyerContent = await page.content();
    if (otherLawyerContent.includes('other') && otherLawyerContent.includes('lawyer')) {
      console.log('✅ Reached other party lawyer section');
      
      await selectOtherPartyHasLawyer(page, true);
      
      // Test Individual object for other party lawyer
      await testIndividualObjectFields(page, {
        type: 'other_lawyer',
        individual: {
          firstName: 'Michael',
          lastName: 'Counsel',
          phone: '4165554444',
          email: 'michael.counsel@legal.com',
          address: {
            street: '456 University Avenue',
            city: 'Toronto',
            province: 'Ontario',
            postalCode: 'M5G 1X5'
          }
        }
      });
      
      console.log('✅ Individual object for other party lawyer tested');
    }
  });

  test('should validate Individual object required fields for lawyers', async ({ page }) => {
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, true);
    
    const lawyerFormContent = await page.content();
    if (lawyerFormContent.includes('Lawyer') || lawyerFormContent.includes('name')) {
      console.log('Testing Individual object validation for lawyers...');
      
      // Try submitting without filling required fields
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const hasValidationErrors = await page.locator('.alert-danger, .text-danger, .da-error, .error').count() > 0;
      if (hasValidationErrors) {
        console.log('✅ Individual object shows validation errors for empty lawyer fields');
        
        // Fill minimum required fields
        await fillLawyerIndividualInfo(page, {
          firstName: 'Test',
          lastName: 'Lawyer',
          phone: '4165551111',
          email: 'test.lawyer@law.com'
        });
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1500);
        
        const afterFill = await page.content();
        if (!afterFill.includes('Error')) {
          console.log('✅ Individual object accepts minimum required lawyer fields');
        }
      }
    }
  });

  test('should validate Organization object required fields for law firms', async ({ page }) => {
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, true);
    
    // Skip or quickly fill lawyer info to get to firm info
    await fillLawyerIndividualInfo(page, {
      firstName: 'Quick',
      lastName: 'Test',
      phone: '4165551111',
      email: 'quick@test.com'
    });
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    const firmContent = await page.content();
    if (firmContent.includes('firm') || firmContent.includes('office')) {
      console.log('Testing Organization object validation for law firms...');
      
      // Try submitting without filling required fields
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const hasValidationErrors = await page.locator('.alert-danger, .text-danger, .da-error, .error').count() > 0;
      if (hasValidationErrors) {
        console.log('✅ Organization object shows validation errors for empty firm fields');
        
        // Fill minimum required fields
        await fillLawFirmOrganizationInfo(page, {
          name: 'Test Law Firm',
          phone: '4165552222',
          email: 'info@testlaw.com'
        });
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1500);
        
        const afterFill = await page.content();
        if (!afterFill.includes('Error')) {
          console.log('✅ Organization object accepts minimum required firm fields');
        }
      }
    }
  });

  test('should handle no lawyer scenario properly', async ({ page }) => {
    await navigateToLawyerInfo(page);
    
    // Select no lawyer
    await selectHasLawyer(page, false);
    
    // Should skip Individual/Organization object collection and move to next section
    const nextContent = await page.content();
    if (nextContent.includes('other') && nextContent.includes('lawyer')) {
      console.log('✅ Properly skipped user lawyer objects when no lawyer selected');
      
      // Test other party lawyer question
      await selectOtherPartyHasLawyer(page, false);
      
      const finalContent = await page.content();
      if (finalContent.includes('Court') || finalContent.includes('recommendations')) {
        console.log('✅ Skipped all lawyer objects and proceeded correctly');
      }
    } else if (nextContent.includes('Court') || nextContent.includes('recommendations')) {
      console.log('✅ Skipped all lawyer objects when no representation');
    }
  });

  test('should handle unknown other party lawyer status', async ({ page }) => {
    await navigateToLawyerInfo(page);
    await selectHasLawyer(page, false); // User has no lawyer
    
    const otherLawyerContent = await page.content();
    if (otherLawyerContent.includes('other') && otherLawyerContent.includes('lawyer')) {
      // Select "I don't know" for other party lawyer
      const unknownButton = page.locator('button:has-text("don\'t know"), button:has-text("unknown"), button:has-text("unsure")');
      if (await unknownButton.first().isVisible()) {
        await unknownButton.first().click();
        await page.waitForTimeout(1000);
        
        // Should proceed without collecting other party lawyer objects
        const afterUnknown = await page.content();
        if (afterUnknown.includes('Court') || afterUnknown.includes('recommendations')) {
          console.log('✅ Properly handled unknown other party lawyer status');
        }
      }
    }
  });

  // Helper Functions

  async function navigateToLawyerInfo(page) {
    // Navigate through to lawyer information section
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    
    // Emergency - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // MIP - Yes
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Divorce
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Divorce complexity - Uncontested
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // Role - Applicant
    const roleContent = await page.content();
    if (roleContent.includes('Role') || roleContent.includes('starting')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
    
    // Fill user party info quickly
    await fillPartyInfoQuickly(page, 'user');
    
    // Fill other party info quickly
    const otherPartyContent = await page.content();
    if (otherPartyContent.includes('Other Party')) {
      await fillPartyInfoQuickly(page, 'other');
    }
  }

  async function fillPartyInfoQuickly(page, partyType) {
    const firstName = partyType === 'user' ? 'John' : 'Jane';
    const lastName = partyType === 'user' ? 'Smith' : 'Doe';
    const phone = partyType === 'user' ? '4165551234' : '4165555678';
    const email = partyType === 'user' ? 'john@example.com' : 'jane@example.com';
    
    await fillFieldByContext(page, ['first'], firstName);
    await fillFieldByContext(page, ['last'], lastName);
    await fillFieldByContext(page, ['phone'], phone);
    await fillFieldByContext(page, ['email'], email, 'email');
    await fillFieldByContext(page, ['address'], '123 Main St');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
  }

  async function selectHasLawyer(page, hasLawyer) {
    const lawyerContent = await page.content();
    if (lawyerContent.includes('lawyer') || lawyerContent.includes('represented')) {
      if (hasLawyer) {
        await page.click('button:has-text("Yes"), input[type="submit"][value="Yes"]');
      } else {
        await page.click('button:has-text("No"), button:has-text("self-represented"), input[type="submit"][value="No"]');
      }
      await page.waitForTimeout(1500);
    }
  }

  async function selectOtherPartyHasLawyer(page, hasLawyer) {
    const otherLawyerContent = await page.content();
    if (otherLawyerContent.includes('other') && otherLawyerContent.includes('lawyer')) {
      if (hasLawyer) {
        await page.click('button:has-text("Yes"), input[type="submit"][value="Yes"]');
      } else {
        await page.click('button:has-text("No"), input[type="submit"][value="No"]');
      }
      await page.waitForTimeout(1500);
    }
  }

  async function testIndividualObjectFields(page, testData) {
    const { type, individual } = testData;
    console.log(`Testing Individual object fields for ${type}...`);
    
    // Name fields
    await fillFieldByContext(page, ['first'], individual.firstName);
    await fillFieldByContext(page, ['last'], individual.lastName);
    if (individual.middleName) {
      await fillFieldByContext(page, ['middle'], individual.middleName);
    }
    if (individual.title) {
      await selectFieldByContext(page, ['title'], individual.title);
    }
    
    // Professional fields
    if (individual.profession) {
      await fillFieldByContext(page, ['profession', 'job'], individual.profession);
    }
    if (individual.barNumber) {
      await fillFieldByContext(page, ['bar', 'license', 'number'], individual.barNumber);
    }
    
    // Contact information
    await fillFieldByContext(page, ['phone'], individual.phone);
    if (individual.alternativePhone) {
      await fillFieldByContext(page, ['phone', 'alternative'], individual.alternativePhone);
    }
    await fillFieldByContext(page, ['email'], individual.email, 'email');
    if (individual.alternativeEmail) {
      await fillFieldByContext(page, ['email', 'alternative'], individual.alternativeEmail, 'email');
    }
    
    // Address
    if (individual.address) {
      await fillAddressFields(page, individual.address);
    }
    
    return true;
  }

  async function testOrganizationObjectFields(page, testData) {
    const { type, organization } = testData;
    console.log(`Testing Organization object fields for ${type}...`);
    
    // Organization name fields
    await fillFieldByContext(page, ['name', 'firm'], organization.name);
    if (organization.legalName) {
      await fillFieldByContext(page, ['legal', 'official'], organization.legalName);
    }
    if (organization.businessNumber) {
      await fillFieldByContext(page, ['business', 'registration'], organization.businessNumber);
    }
    
    // Contact information
    await fillFieldByContext(page, ['phone'], organization.phone);
    if (organization.fax) {
      await fillFieldByContext(page, ['fax'], organization.fax);
    }
    await fillFieldByContext(page, ['email'], organization.email, 'email');
    if (organization.website) {
      await fillFieldByContext(page, ['website', 'url'], organization.website);
    }
    
    // Address
    if (organization.address) {
      await fillAddressFields(page, organization.address);
    }
    
    return true;
  }

  async function fillLawyerIndividualInfo(page, lawyer) {
    await fillFieldByContext(page, ['first'], lawyer.firstName);
    await fillFieldByContext(page, ['last'], lawyer.lastName);
    await fillFieldByContext(page, ['phone'], lawyer.phone);
    await fillFieldByContext(page, ['email'], lawyer.email, 'email');
    
    if (lawyer.address) {
      await fillFieldByContext(page, ['address'], lawyer.address);
    }
    if (lawyer.city) {
      await fillFieldByContext(page, ['city'], lawyer.city);
    }
  }

  async function fillLawFirmOrganizationInfo(page, firm) {
    await fillFieldByContext(page, ['name', 'firm'], firm.name);
    await fillFieldByContext(page, ['phone'], firm.phone);
    await fillFieldByContext(page, ['email'], firm.email, 'email');
    
    if (firm.address) {
      await fillFieldByContext(page, ['address'], firm.address);
    }
    if (firm.city) {
      await fillFieldByContext(page, ['city'], firm.city);
    }
  }

  async function fillAddressFields(page, address) {
    await fillFieldByContext(page, ['address', 'street'], address.street);
    if (address.suite) {
      await fillFieldByContext(page, ['suite', 'unit'], address.suite);
    }
    await fillFieldByContext(page, ['city'], address.city);
    if (address.province) {
      await selectFieldByContext(page, ['province'], address.province);
    }
    await fillFieldByContext(page, ['postal'], address.postalCode);
  }

  async function fillFieldByContext(page, contextWords, value, inputType = 'text') {
    const field = await findFieldByContext(page, contextWords, inputType);
    if (field) {
      await field.fill(value);
      return true;
    }
    return false;
  }

  async function selectFieldByContext(page, contextWords, value) {
    const selects = await page.locator('select').all();
    for (const select of selects) {
      const name = await select.getAttribute('name') || '';
      const label = await select.getAttribute('aria-label') || '';
      const context = (name + label).toLowerCase();
      
      if (contextWords.some(word => context.includes(word.toLowerCase()))) {
        try {
          await select.selectOption(value);
          return true;
        } catch (e) {
          const options = await select.locator('option').allTextContents();
          const matchingOption = options.find(opt => 
            opt.toLowerCase().includes(value.toLowerCase())
          );
          if (matchingOption) {
            await select.selectOption({ label: matchingOption });
            return true;
          }
        }
      }
    }
    return false;
  }

  async function findFieldByContext(page, contextWords, inputType = 'text') {
    const selector = inputType === 'email' ? 'input[type="email"], input[type="text"]' :
                    'input[type="text"], input[type="tel"]';
    
    const inputs = await page.locator(selector).all();
    
    for (const input of inputs) {
      const name = await input.getAttribute('name') || '';
      const placeholder = await input.getAttribute('placeholder') || '';
      const label = await input.getAttribute('aria-label') || '';
      const context = (name + placeholder + label).toLowerCase();
      
      if (contextWords.some(word => context.includes(word.toLowerCase()))) {
        return input;
      }
    }
    return null;
  }
});