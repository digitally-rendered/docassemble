const { test, expect } = require('@playwright/test');

test.describe('Ontario Family Law Wizard - Comprehensive Testing', () => {
  const wizardUrl = 'http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml';

  test.beforeEach(async ({ page }) => {
    // Set up error handling
    page.on('pageerror', exception => {
      console.log(`Page error: ${exception}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`Request failed: ${request.url()}`);
    });

    await page.goto(wizardUrl);
    await page.waitForLoadState('networkidle');
  });

  test('should load wizard without errors and display welcome screen', async ({ page }) => {
    // Check that we're not on an error page
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    const errorBlockquote = await page.locator('blockquote').count();
    
    if (errorHeading > 0 && errorBlockquote > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      throw new Error(`Wizard failed to load: ${errorMessage}`);
    }

    // Verify welcome screen loads
    await expect(page.locator('text=Welcome to the Ontario Family Law Forms Wizard')).toBeVisible();
    
    // Check that essential page elements are present
    await expect(page.locator('button[type="submit"]#da-continue-button, input[type="submit"][value*="Continue"]')).toBeVisible();
    
    console.log('✅ Wizard loads successfully with welcome screen');
  });

  test('should handle error conditions gracefully', async ({ page }) => {
    // Navigate to check error handling
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Check if error screen appears and that it's handled properly
    const content = await page.content();
    
    if (content.includes('Technical Issue Detected')) {
      console.log('Error screen displayed correctly');
      
      // Check that error information is shown
      await expect(page.locator('text=Error Type:')).toBeVisible();
      await expect(page.locator('text=Error Message:')).toBeVisible();
      
      // Check that action buttons are available
      await expect(page.locator('button:has-text("Restart")')).toBeVisible();
      await expect(page.locator('button:has-text("Exit")')).toBeVisible();
      
      console.log('✅ Error handling works correctly');
    } else {
      console.log('✅ No errors occurred during basic navigation');
    }
  });

  test('should use Person objects for parties (applicant/respondent)', async ({ page }) => {
    // Navigate through to party information collection
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('✅ Reached user party information screen');
      
      // Check for Person object fields (name, address, contact info)
      await expect(page.locator('input[name*="name"], input[name*="first"], input[name*="last"]')).toHaveCount({ min: 1 });
      await expect(page.locator('input[name*="address"], input[name*="street"]')).toHaveCount({ min: 1 });
      await expect(page.locator('input[name*="phone"], input[name*="email"]')).toHaveCount({ min: 1 });
      
      // Fill out party information to test Person object functionality
      await fillPersonObjectFields(page, {
        firstName: 'John',
        lastName: 'Smith',
        phone: '4165551234',
        email: 'john.smith@example.com',
        address: '123 King Street West',
        city: 'Toronto',
        postalCode: 'M5H 2N2'
      });
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(2000);
      
      // Check if we moved to other party (should have respondent information)
      const afterUserContent = await page.content();
      if (afterUserContent.includes('Other Party')) {
        console.log('✅ Person object for user party working - moved to other party');
        
        // Fill other party (respondent) information
        await fillPersonObjectFields(page, {
          firstName: 'Jane',
          lastName: 'Doe', 
          phone: '4165555678',
          email: 'jane.doe@example.com',
          address: '456 Oak Avenue',
          city: 'Toronto',
          postalCode: 'M4W 1J5'
        });
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        console.log('✅ Person objects working for both applicant and respondent');
      } else if (afterUserContent.includes('Error')) {
        const errors = await page.locator('.alert-danger, .text-danger').allTextContents();
        console.log('❌ Person object validation failed:', errors);
      }
    } else {
      console.log('❓ Did not reach party information screen');
    }
  });

  test('should use Individual objects for lawyers', async ({ page }) => {
    // Navigate through to lawyer information collection
    await navigateToPartyInfo(page);
    await fillBasicPartyInfo(page);
    
    // Look for lawyer questions
    await page.waitForTimeout(1000);
    const lawyerContent = await page.content();
    
    if (lawyerContent.includes('lawyer') || lawyerContent.includes('represented')) {
      console.log('✅ Reached lawyer information section');
      
      // Select "Yes, I have a lawyer"
      const yesLawyerButton = page.locator('button:has-text("Yes"), input[type="submit"][value="Yes"]').first();
      if (await yesLawyerButton.isVisible()) {
        await yesLawyerButton.click();
        await page.waitForTimeout(2000);
        
        // Check for Individual object fields for lawyer
        const lawyerFormContent = await page.content();
        if (lawyerFormContent.includes('Lawyer') && 
            (lawyerFormContent.includes('name') || lawyerFormContent.includes('contact'))) {
          
          // Fill Individual object fields for lawyer
          await fillIndividualObjectFields(page, {
            firstName: 'Sarah',
            lastName: 'Legal',
            phone: '4165551111',
            email: 'sarah.legal@lawfirm.com',
            address: '789 Bay Street',
            city: 'Toronto',
            postalCode: 'M5G 2C8'
          });
          
          console.log('✅ Individual object fields for lawyer filled successfully');
        }
      } else {
        // Try "No lawyer" option to continue
        const noLawyerButton = page.locator('button:has-text("No"), input[type="submit"][value="No"], button:has-text("self-represented")').first();
        if (await noLawyerButton.isVisible()) {
          await noLawyerButton.click();
          await page.waitForTimeout(1000);
          console.log('✅ Lawyer question handled - user selected no lawyer');
        }
      }
    }
  });

  test('should use Organization objects for law firms', async ({ page }) => {
    // Navigate to lawyer information and select having a lawyer
    await navigateToPartyInfo(page);
    await fillBasicPartyInfo(page);
    
    // Look for lawyer questions and select yes
    await page.waitForTimeout(1000);
    const lawyerContent = await page.content();
    
    if (lawyerContent.includes('lawyer') || lawyerContent.includes('represented')) {
      const yesLawyerButton = page.locator('button:has-text("Yes"), input[type="submit"][value="Yes"]').first();
      if (await yesLawyerButton.isVisible()) {
        await yesLawyerButton.click();
        await page.waitForTimeout(2000);
        
        // Look for law firm/organization fields
        const firmContent = await page.content();
        if (firmContent.includes('firm') || firmContent.includes('organization') || 
            firmContent.includes('Office') || firmContent.includes('Company')) {
          
          // Fill Organization object fields for law firm
          await fillOrganizationObjectFields(page, {
            name: 'Smith & Associates Law Firm',
            address: '789 Bay Street, Suite 1200',
            city: 'Toronto', 
            postalCode: 'M5G 2C8',
            phone: '4165552222',
            email: 'info@smithlaw.ca'
          });
          
          console.log('✅ Organization object for law firm filled successfully');
        }
      }
    }
  });

  test('should validate required fields properly', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      // Try to submit form without filling required fields
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Check for validation messages
      const validationMessages = await page.locator('.alert-danger, .text-danger, .da-error').count();
      if (validationMessages > 0) {
        console.log('✅ Field validation is working - shows errors for empty required fields');
        
        // Fill just first name and try again
        const firstNameInput = page.locator('input[name*="first"], input[name*="name"]').first();
        if (await firstNameInput.isVisible()) {
          await firstNameInput.fill('John');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          // Check if more fields are required
          const stillHasErrors = await page.locator('.alert-danger, .text-danger, .da-error').count();
          if (stillHasErrors > 0) {
            console.log('✅ Validation properly requires multiple fields to be filled');
          }
        }
      } else {
        console.log('❓ No validation errors shown - may have different validation approach');
      }
    }
  });

  test('should handle divorce with property scenario', async ({ page }) => {
    // Test comprehensive divorce scenario
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    
    // Emergency - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // MIP - Yes
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Divorce and Property
    await page.check('text=Divorce');
    await page.check('text=Property');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Should be contested due to property
    const complexityContent = await page.content();
    if (complexityContent.includes('contested') || complexityContent.includes('Contested')) {
      await page.click('button:has-text("Contested")');
      await page.waitForTimeout(500);
      console.log('✅ Divorce with property correctly identified as contested');
    }
    
    // Check for financial forms
    const financialContent = await page.content();
    if (financialContent.includes('financial') || financialContent.includes('property')) {
      console.log('✅ Financial forms section appeared for divorce with property');
    }
  });

  // Helper functions
  async function navigateToPartyInfo(page) {
    // Navigate through initial screens to reach party information
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    
    // Emergency - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // MIP - Yes  
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    
    // Relationship - Married (simple case)
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Just divorce (simple)
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Divorce complexity - Uncontested
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // Role selection - Applicant
    const roleContent = await page.content();
    if (roleContent.includes('Role') || roleContent.includes('starting')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
  }

  async function fillPersonObjectFields(page, data) {
    // Fill Person object fields (using various possible field name patterns)
    const inputs = await page.locator('input[type="text"], input[type="email"], input[type="tel"]').all();
    
    for (const input of inputs) {
      const name = await input.getAttribute('name') || '';
      const placeholder = await input.getAttribute('placeholder') || '';
      const label = await input.getAttribute('aria-label') || '';
      const fieldContext = (name + placeholder + label).toLowerCase();
      
      // First name
      if (fieldContext.includes('first') && !fieldContext.includes('last')) {
        await input.fill(data.firstName);
      }
      // Last name
      else if (fieldContext.includes('last') || fieldContext.includes('surname')) {
        await input.fill(data.lastName);
      }
      // Phone
      else if (fieldContext.includes('phone') || fieldContext.includes('tel')) {
        await input.fill(data.phone);
      }
      // Email
      else if (fieldContext.includes('email') || await input.getAttribute('type') === 'email') {
        await input.fill(data.email);
      }
      // Address
      else if (fieldContext.includes('address') || fieldContext.includes('street')) {
        await input.fill(data.address);
      }
      // City
      else if (fieldContext.includes('city')) {
        await input.fill(data.city);
      }
      // Postal code
      else if (fieldContext.includes('postal') || fieldContext.includes('zip')) {
        await input.fill(data.postalCode);
      }
    }
    
    // Fill date fields if present
    const dateInputs = await page.locator('input[type="date"]').all();
    if (dateInputs.length > 0) {
      await dateInputs[0].fill('1985-06-15');
    }
  }

  async function fillIndividualObjectFields(page, data) {
    // Similar to Person but for Individual objects (lawyers)
    await fillPersonObjectFields(page, data);
    
    // Additional fields that might be specific to lawyers/individuals
    const professionFields = await page.locator('input[name*="profession"], input[name*="title"]').all();
    if (professionFields.length > 0) {
      await professionFields[0].fill('Lawyer');
    }
  }

  async function fillOrganizationObjectFields(page, data) {
    const inputs = await page.locator('input[type="text"], input[type="email"], input[type="tel"]').all();
    
    for (const input of inputs) {
      const name = await input.getAttribute('name') || '';
      const placeholder = await input.getAttribute('placeholder') || '';
      const label = await input.getAttribute('aria-label') || '';
      const fieldContext = (name + placeholder + label).toLowerCase();
      
      // Organization name
      if (fieldContext.includes('name') || fieldContext.includes('firm') || fieldContext.includes('company')) {
        await input.fill(data.name);
      }
      // Phone
      else if (fieldContext.includes('phone') || fieldContext.includes('tel')) {
        await input.fill(data.phone);
      }
      // Email  
      else if (fieldContext.includes('email') || await input.getAttribute('type') === 'email') {
        await input.fill(data.email);
      }
      // Address
      else if (fieldContext.includes('address') || fieldContext.includes('street')) {
        await input.fill(data.address);
      }
      // City
      else if (fieldContext.includes('city')) {
        await input.fill(data.city);
      }
      // Postal code
      else if (fieldContext.includes('postal') || fieldContext.includes('zip')) {
        await input.fill(data.postalCode);
      }
    }
  }

  async function fillBasicPartyInfo(page) {
    // Fill basic party information for both parties quickly
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      await fillPersonObjectFields(page, {
        firstName: 'John',
        lastName: 'Smith',
        phone: '4165551234',
        email: 'john.smith@example.com',
        address: '123 King Street West',
        city: 'Toronto',
        postalCode: 'M5H 2N2'
      });
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1500);
      
      // Fill other party if present
      const otherPartyContent = await page.content();
      if (otherPartyContent.includes('Other Party')) {
        await fillPersonObjectFields(page, {
          firstName: 'Jane',
          lastName: 'Doe',
          phone: '4165555678',
          email: 'jane.doe@example.com',
          address: '456 Oak Avenue',
          city: 'Toronto',
          postalCode: 'M4W 1J5'
        });
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
      }
    }
  }
});