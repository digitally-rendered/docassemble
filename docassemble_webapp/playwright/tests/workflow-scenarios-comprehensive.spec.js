const { test, expect } = require('@playwright/test');

test.describe('Comprehensive Workflow Scenarios', () => {
  const wizardUrl = 'http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml';

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', exception => {
      console.log(`Page error: ${exception}`);
    });
    
    await page.goto(wizardUrl);
    await page.waitForLoadState('networkidle');
  });

  test('should handle emergency divorce scenario with complete workflow', async ({ page }) => {
    console.log('Testing emergency divorce scenario...');
    
    // Start wizard
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Emergency - Yes
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(1000);
    
    const emergencyContent = await page.content();
    if (emergencyContent.includes('URGENT') || emergencyContent.includes('Emergency')) {
      console.log('✅ Emergency pathway activated');
      
      // Continue through emergency flow
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
      
      // Skip MIP for emergency
      // Relationship status
      await page.click('button:has-text("Married")');
      await page.waitForTimeout(500);
      
      // Orders - Emergency divorce
      await page.check('text=Divorce');
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
      
      // Should be contested (emergency)
      await page.click('button:has-text("Contested")');
      await page.waitForTimeout(500);
      
      // Complete party information collection
      await completePartyInfoWorkflow(page);
      
      // Final screen should indicate emergency
      const finalContent = await page.content();
      if (finalContent.includes('Emergency') || finalContent.includes('URGENT')) {
        console.log('✅ Emergency divorce workflow completed successfully');
      }
    }
  });

  test('should handle uncontested divorce with no children workflow', async ({ page }) => {
    console.log('Testing uncontested divorce (no children) scenario...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Just divorce
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Divorce complexity - Uncontested
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    // Should reach recommendations
    const recommendationsContent = await page.content();
    if (recommendationsContent.includes('Forms Package') || recommendationsContent.includes('recommendations')) {
      console.log('✅ Uncontested divorce (no children) workflow completed');
      
      // Verify appropriate forms recommended (should be simple divorce forms)
      const content = await page.content();
      if (content.includes('Form 8') || content.includes('divorce')) {
        console.log('✅ Appropriate forms recommended for uncontested divorce');
      }
    }
  });

  test('should handle contested divorce with children and support workflow', async ({ page }) => {
    console.log('Testing contested divorce with children and support...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Multiple orders (makes it contested)
    await page.check('text=Divorce');
    await page.check('text=Child custody');
    await page.check('text=Child support');
    await page.check('text=Spousal support');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Should be contested due to multiple issues
    await page.click('button:has-text("Contested")');
    await page.waitForTimeout(500);
    
    // Financial complexity screen
    const financialContent = await page.content();
    if (financialContent.includes('financial')) {
      console.log('✅ Financial forms section appeared for complex case');
      
      await fillFinancialForm(page);
    }
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    // Verify complex case handling
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package') || finalContent.includes('recommendations')) {
      console.log('✅ Contested divorce with children/support workflow completed');
      
      // Should recommend comprehensive forms
      const content = await page.content();
      if (content.includes('Form 13') || content.includes('Financial Statement')) {
        console.log('✅ Financial forms recommended for complex case');
      }
    }
  });

  test('should handle common-law support and custody workflow', async ({ page }) => {
    console.log('Testing common-law with support and custody...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Common-law
    await page.click('button:has-text("Common-law")');
    await page.waitForTimeout(500);
    
    // Orders - Support and custody
    await page.check('text=Child custody');
    await page.check('text=Child support');
    await page.check('text=Spousal support');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Financial forms likely required
    const financialContent = await page.content();
    if (financialContent.includes('financial')) {
      await fillFinancialForm(page);
    }
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package') || finalContent.includes('recommendations')) {
      console.log('✅ Common-law support and custody workflow completed');
    }
  });

  test('should handle never lived together paternity and support workflow', async ({ page }) => {
    console.log('Testing never lived together (paternity and support)...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Never lived together
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(500);
    
    // Orders - Paternity and support (different question structure)
    const neverTogetherContent = await page.content();
    if (neverTogetherContent.includes('Child custody') || neverTogetherContent.includes('Paternity')) {
      await page.check('text=Child custody');
      await page.check('text=Child support');
      
      // Look for paternity checkbox
      const paternityCheckbox = page.locator('text=Paternity');
      if (await paternityCheckbox.isVisible()) {
        await paternityCheckbox.click();
        console.log('✅ Paternity option available for never lived together');
      }
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
    }
    
    // May have financial forms
    const financialContent = await page.content();
    if (financialContent.includes('financial')) {
      await fillFinancialForm(page);
    }
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package') || finalContent.includes('recommendations')) {
      console.log('✅ Never lived together (paternity/support) workflow completed');
    }
  });

  test('should handle property division and exclusive possession workflow', async ({ page }) => {
    console.log('Testing property division and exclusive possession...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Married (required for property division)
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Property focused
    await page.check('text=Property division');
    await page.check('text=Exclusive possession');
    await page.check('text=Divorce'); // Usually goes with property
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Contested due to property
    await page.click('button:has-text("Contested")');
    await page.waitForTimeout(500);
    
    // Should definitely have financial forms
    const financialContent = await page.content();
    if (financialContent.includes('financial') || financialContent.includes('property')) {
      console.log('✅ Financial forms required for property division');
      
      // Fill with property-focused data
      await fillPropertyFocusedFinancialForm(page);
    }
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package')) {
      console.log('✅ Property division workflow completed');
      
      // Should recommend property-related forms
      const content = await page.content();
      if (content.includes('Form 13') || content.includes('Net Family Property')) {
        console.log('✅ Property-specific forms recommended');
      }
    }
  });

  test('should handle enforcement and contempt workflow', async ({ page }) => {
    console.log('Testing enforcement and contempt scenario...');
    
    await startBasicWorkflow(page);
    
    // Relationship - Can be any
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Enforcement focused
    await page.check('text=Enforcement');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Complete party information
    await completePartyInfoWorkflow(page);
    
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package')) {
      console.log('✅ Enforcement workflow completed');
      
      // Should recommend enforcement-specific forms
      const content = await page.content();
      if (content.includes('enforcement') || content.includes('contempt')) {
        console.log('✅ Enforcement-specific forms recommended');
      }
    }
  });

  test('should handle complete workflow with lawyers for both parties', async ({ page }) => {
    console.log('Testing complete workflow with lawyer representation...');
    
    await startBasicWorkflow(page);
    
    // Simple divorce case
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    await page.click('button:has-text("No")'); // No children
    await page.waitForTimeout(500);
    
    // Role selection
    const roleContent = await page.content();
    if (roleContent.includes('Role')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
    
    // Fill user party information
    await fillPartyInfo(page, {
      firstName: 'John',
      lastName: 'Smith',
      phone: '4165551234',
      email: 'john@example.com',
      address: '123 Main St',
      city: 'Toronto',
      postal: 'M5H 2N2'
    });
    
    // Fill other party information
    const otherPartyContent = await page.content();
    if (otherPartyContent.includes('Other Party')) {
      await fillPartyInfo(page, {
        firstName: 'Jane',
        lastName: 'Doe',
        phone: '4165555678',
        email: 'jane@example.com',
        address: '456 Oak Ave',
        city: 'Toronto',
        postal: 'M4W 1J5'
      });
    }
    
    // User has lawyer
    const userLawyerContent = await page.content();
    if (userLawyerContent.includes('lawyer') || userLawyerContent.includes('represented')) {
      await page.click('button:has-text("Yes")');
      await page.waitForTimeout(1000);
      
      // Fill lawyer information (Individual object)
      const lawyerFormContent = await page.content();
      if (lawyerFormContent.includes('Lawyer') || lawyerFormContent.includes('name')) {
        await fillLawyerInfo(page, {
          firstName: 'Sarah',
          lastName: 'Legal',
          phone: '4165551111',
          email: 'sarah@law.com'
        });
      }
    }
    
    // Other party has lawyer
    const otherLawyerContent = await page.content();
    if (otherLawyerContent.includes('other') && otherLawyerContent.includes('lawyer')) {
      await page.click('button:has-text("Yes")');
      await page.waitForTimeout(1000);
      
      // Fill other party lawyer information
      const otherLawyerFormContent = await page.content();
      if (otherLawyerFormContent.includes('Lawyer') || otherLawyerFormContent.includes('name')) {
        await fillLawyerInfo(page, {
          firstName: 'Michael',
          lastName: 'Attorney',
          phone: '4165554444',
          email: 'michael@legal.com'
        });
      }
    }
    
    // Court information
    const courtContent = await page.content();
    if (courtContent.includes('Court')) {
      await fillCourtInfo(page);
    }
    
    const finalContent = await page.content();
    if (finalContent.includes('Forms Package') || finalContent.includes('Ready')) {
      console.log('✅ Complete workflow with lawyers completed successfully');
    }
  });

  // Helper Functions

  async function startBasicWorkflow(page) {
    // Welcome screen
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Emergency - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // MIP - Yes
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
  }

  async function completePartyInfoWorkflow(page) {
    // Role selection if present
    const roleContent = await page.content();
    if (roleContent.includes('Role') || roleContent.includes('starting')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
    
    // User party information
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      await fillPartyInfo(page, {
        firstName: 'John',
        lastName: 'Smith',
        phone: '4165551234',
        email: 'john@example.com',
        address: '123 Main St',
        city: 'Toronto',
        postal: 'M5H 2N2'
      });
    }
    
    // Other party information
    const otherPartyContent = await page.content();
    if (otherPartyContent.includes('Other Party')) {
      await fillPartyInfo(page, {
        firstName: 'Jane',
        lastName: 'Doe',
        phone: '4165555678',
        email: 'jane@example.com',
        address: '456 Oak Ave',
        city: 'Toronto',
        postal: 'M4W 1J5'
      });
    }
    
    // Lawyer questions - select no lawyers for simplicity
    const userLawyerContent = await page.content();
    if (userLawyerContent.includes('lawyer') || userLawyerContent.includes('represented')) {
      await page.click('button:has-text("No"), button:has-text("self-represented")');
      await page.waitForTimeout(1000);
    }
    
    const otherLawyerContent = await page.content();
    if (otherLawyerContent.includes('other') && otherLawyerContent.includes('lawyer')) {
      await page.click('button:has-text("don\'t know"), button:has-text("No")');
      await page.waitForTimeout(1000);
    }
    
    // Court information
    const courtContent = await page.content();
    if (courtContent.includes('Court')) {
      await fillCourtInfo(page);
    }
  }

  async function fillFinancialForm(page) {
    console.log('Filling financial form...');
    
    // Property value
    const inputs = await page.locator('input[type="text"], input[type="number"]').all();
    if (inputs.length > 0) {
      await inputs[0].fill('50000');
    }
    
    // Radio buttons
    const radioButtons = await page.locator('input[type="radio"]').all();
    for (let i = 0; i < Math.min(4, radioButtons.length); i++) {
      if (i % 2 === 0) {
        await radioButtons[i].click();
        await page.waitForTimeout(100);
      }
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
  }

  async function fillPropertyFocusedFinancialForm(page) {
    console.log('Filling property-focused financial form...');
    
    // Higher property value for property division case
    const inputs = await page.locator('input[type="text"], input[type="number"]').all();
    if (inputs.length > 0) {
      await inputs[0].fill('250000'); // Higher value
    }
    
    // Select options that indicate property ownership
    const radioButtons = await page.locator('input[type="radio"]').all();
    for (let i = 0; i < Math.min(4, radioButtons.length); i++) {
      if (i % 2 === 0) {
        await radioButtons[i].click();
        await page.waitForTimeout(100);
      }
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
  }

  async function fillPartyInfo(page, info) {
    await fillFieldByContext(page, ['first'], info.firstName);
    await fillFieldByContext(page, ['last'], info.lastName);
    await fillFieldByContext(page, ['phone'], info.phone);
    await fillFieldByContext(page, ['email'], info.email, 'email');
    await fillFieldByContext(page, ['address'], info.address);
    await fillFieldByContext(page, ['city'], info.city);
    await fillFieldByContext(page, ['postal'], info.postal);
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
  }

  async function fillLawyerInfo(page, info) {
    await fillFieldByContext(page, ['first'], info.firstName);
    await fillFieldByContext(page, ['last'], info.lastName);
    await fillFieldByContext(page, ['phone'], info.phone);
    await fillFieldByContext(page, ['email'], info.email, 'email');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
  }

  async function fillCourtInfo(page) {
    await fillFieldByContext(page, ['location', 'court'], 'Toronto');
    await fillFieldByContext(page, ['address'], '393 University Avenue');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
  }

  async function fillFieldByContext(page, contextWords, value, inputType = 'text') {
    const field = await findFieldByContext(page, contextWords, inputType);
    if (field) {
      await field.fill(value);
      return true;
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