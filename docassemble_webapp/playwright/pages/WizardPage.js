const { expect } = require('@playwright/test');

/**
 * Page Object Model for the Ontario Family Law Forms Wizard
 * Provides methods to interact with the wizard's various screens and elements
 */
class WizardPage {
  constructor(page) {
    this.page = page;
    
    // Common selectors for docassemble
    this.continueButton = 'button[type="submit"]#da-continue-button, input[type="submit"][value*="Continue"], button:has-text("Continue")';
    this.yesButton = 'input[type="submit"][value="Yes"], button:has-text("Yes")';
    this.noButton = 'input[type="submit"][value="No"], button:has-text("No")';
    this.questionText = '#daMainQuestion, .da-question-text, .da-form-title h1';
    this.subquestionText = '.da-subquestion, .da-form-subtitle';
    
    // Specific selectors for wizard steps
    this.emergencyYes = 'button[type="submit"]:has-text("Yes, this is an emergency")';
    this.emergencyNo = 'button[type="submit"]:has-text("No, this is not an emergency")';
    this.mipYes = 'button[type="submit"]:has-text("Yes, I have my certificate")';
    this.mipNo = 'button[type="submit"]:has-text("No, I need to attend")';
    this.mipUnsure = 'button[type="submit"]:has-text("not sure")';
    
    // Relationship status buttons
    this.marriedButton = 'button[type="submit"]:has-text("Married")';
    this.commonLawButton = 'button[type="submit"]:has-text("Common-law")';
    this.neverTogetherButton = 'button[type="submit"]:has-text("Never lived together")';
    
    // Divorce complexity buttons
    this.uncontestedButton = 'button[type="submit"]:has-text("Uncontested")';
    this.contestedButton = 'button[type="submit"]:has-text("Contested")';
    
    // Checkboxes for orders sought
    this.seekingDivorceCheckbox = 'input[name="seeking_divorce"]';
    this.seekingCustodyCheckbox = 'input[name="seeking_custody"]';
    this.seekingChildSupportCheckbox = 'input[name="seeking_child_support"]';
    this.seekingSpousalSupportCheckbox = 'input[name="seeking_spousal_support"]';
    this.seekingPropertyCheckbox = 'input[name="seeking_property"]';
    this.seekingExclusivePossessionCheckbox = 'input[name="seeking_exclusive_possession"]';
    this.seekingRestrainingOrderCheckbox = 'input[name="seeking_restraining_order"]';
    this.seekingEnforcementCheckbox = 'input[name="seeking_enforcement"]';
    this.seekingOtherCheckbox = 'input[name="seeking_other"]';
    
    // Never together specific checkboxes
    this.neverTogetherCustodyCheckbox = 'input[name="never_together_custody"]';
    this.neverTogetherChildSupportCheckbox = 'input[name="never_together_child_support"]';
    this.neverTogetherPaternityCheckbox = 'input[name="never_together_paternity"]';
    this.neverTogetherRestrainingCheckbox = 'input[name="never_together_restraining"]';
    this.neverTogetherOtherCheckbox = 'input[name="never_together_other"]';
    
    // Financial form fields
    this.propertyValueField = 'input[name="property_value"]';
    this.supportInvolvedYes = 'input[name="support_involved"][value="True"]';
    this.supportInvolvedNo = 'input[name="support_involved"][value="False"]';
    this.businessOwnerYes = 'input[name="business_owner"][value="True"]';
    this.businessOwnerNo = 'input[name="business_owner"][value="False"]';
    this.pensionInvolvedYes = 'input[name="pension_involved"][value="True"]';
    this.pensionInvolvedNo = 'input[name="pension_involved"][value="False"]';
  }

  /**
   * Navigate to the wizard
   */
  async goto() {
    await this.page.goto('/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await this.page.waitForLoadState('networkidle');
    
    // Check for interview errors on initial load
    await this.checkForInterviewError();
  }

  /**
   * Check if the interview has crashed with an error
   */
  async checkForInterviewError() {
    // Check if we're on the error page
    const errorHeading = await this.page.locator('h1:has-text("Error")').count();
    const errorBlockquote = await this.page.locator('blockquote').count();
    
    if (errorHeading > 0 && errorBlockquote > 0) {
      const errorMessage = await this.page.locator('blockquote').textContent();
      throw new Error(`Interview crashed: ${errorMessage}`);
    }
  }

  /**
   * Wait for a specific question to appear (flexible matching)
   * Supports partial matching for questions that may vary slightly
   */
  async waitForQuestion(expectedText, options = {}) {
    const { partial = false, timeout = 10000 } = options;
    
    // First check for interview errors
    await this.checkForInterviewError();
    
    if (partial) {
      // For partial matching, check if the question contains the expected text
      await expect(this.page.locator(this.questionText)).toContainText(expectedText, { timeout });
    } else {
      // For exact matching, use the original behavior
      await expect(this.page.locator(this.questionText)).toContainText(expectedText, { timeout });
    }
  }

  /**
   * Wait for question containing certain keywords
   */
  async waitForQuestionContaining(keywords, maxRetries = 10) {
    for (let i = 0; i < maxRetries; i++) {
      // Check for interview errors
      await this.checkForInterviewError();
      
      // Wait for the question element to be visible
      await this.page.waitForSelector(this.questionText, { timeout: 10000 });
      
      // Get the actual question text
      const questionText = await this.page.locator(this.questionText).textContent();
      
      // Also check the subquestion if it exists
      let subquestionText = '';
      const subquestionSelector = '.question-subquestionText, .da-subquestion';
      const subquestionElement = await this.page.locator(subquestionSelector);
      if (await subquestionElement.count() > 0) {
        subquestionText = await subquestionElement.textContent();
      }
      
      const fullText = `${questionText} ${subquestionText}`.toLowerCase();
      
      // Check if any of the keywords are in the question or subquestion
      for (const keyword of keywords) {
        if (fullText.includes(keyword.toLowerCase().replace('?', ''))) {
          return true;
        }
      }
      
      // If keywords not found yet, wait a bit and retry
      if (i < maxRetries - 1) {
        await this.page.waitForTimeout(500);
      }
    }
    
    // If we get here after all retries, none of the keywords were found
    const questionText = await this.page.locator(this.questionText).textContent();
    throw new Error(`Question "${questionText}" (with subquestion) does not contain any of: ${keywords.join(', ')}`);
  }

  /**
   * Click continue button and wait for next screen
   */
  async clickContinue() {
    await this.page.locator(this.continueButton).click();
    await this.page.waitForLoadState('networkidle');
    // Small delay to ensure docassemble has processed the request
    await this.page.waitForTimeout(500);
    
    // Check for interview errors after navigation
    await this.checkForInterviewError();
  }

  /**
   * Handle the introduction screen
   */
  async handleIntroduction() {
    await this.waitForQuestion('Welcome to the Ontario Family Law Forms Wizard');
    await this.clickContinue();
  }

  /**
   * Handle emergency situation question
   */
  async handleEmergencyQuestion(isEmergency) {
    await this.waitForQuestion('Is this an emergency situation?');
    if (isEmergency) {
      await this.page.locator(this.emergencyYes).click();
    } else {
      await this.page.locator(this.emergencyNo).click();
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Handle emergency forms screen (just continue)
   */
  async handleEmergencyFormsScreen() {
    await this.waitForQuestion('URGENT: Emergency Filing Required');
    await this.clickContinue();
  }

  /**
   * Handle MIP information screen
   */
  async handleMipQuestion(mipStatus) {
    await this.waitForQuestion('Mandatory Information Program');
    
    switch (mipStatus) {
      case 'completed':
        await this.page.locator(this.mipYes).click();
        break;
      case 'not_completed':
        await this.page.locator(this.mipNo).click();
        break;
      case 'unsure':
        await this.page.locator(this.mipUnsure).click();
        break;
    }
    await this.page.waitForLoadState('networkidle');
    
    // Handle the follow-up MIP information screen
    await this.waitForQuestion('MIP Session Information');
    await this.clickContinue();
  }

  /**
   * Handle relationship status question
   */
  async handleRelationshipStatus(status) {
    await this.waitForQuestion('What is your relationship status?');
    
    switch (status) {
      case 'married':
        await this.page.locator(this.marriedButton).click();
        break;
      case 'common_law':
        await this.page.locator(this.commonLawButton).click();
        break;
      case 'never_together':
        await this.page.locator(this.neverTogetherButton).click();
        break;
    }
    await this.page.waitForLoadState('networkidle');
    
    // Add explicit wait for navigation to ensure we moved to next question
    await this.page.waitForTimeout(1000);
  }

  /**
   * Handle divorce question for married couples
   */
  async handleDivorceQuestion(seekingDivorce) {
    await this.waitForQuestion('Are you seeking a divorce?');
    
    if (seekingDivorce) {
      await this.page.locator('button:has-text("Yes, I want a divorce")').click();
    } else {
      await this.page.locator('button:has-text("No, just other orders")').click();
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Handle orders sought for married/common-law couples
   * Updated to handle both "What orders are you seeking?" and "What other orders are you seeking?"
   */
  async handleOrdersSought(orders) {
    // Don't wait for networkidle here as we should already be on the right page
    // Just wait for the question to appear
    await this.waitForQuestionContaining(['orders are you seeking', 'orders do you need', 'family law orders']);
    
    // Click on the label text to check/uncheck boxes since docassemble uses dynamic names
    // Use more flexible selectors that work with checkbox labels
    // Note: Divorce is handled separately for married couples, so we skip it here
    if (orders.divorce && !orders.divorce_handled) {
      await this.page.click('label:has-text("Divorce"), text=Divorce');
    }
    if (orders.custody) {
      await this.page.click('label:has-text("Child custody"), text=Child custody');
    }
    if (orders.child_support) {
      await this.page.click('label:has-text("Child support"), text=Child support');
    }
    if (orders.spousal_support) {
      await this.page.click('label:has-text("Spousal support"), text=Spousal support');
    }
    if (orders.property) {
      await this.page.click('label:has-text("Property division"), text=Property division');
    }
    if (orders.exclusive_possession) {
      await this.page.click('label:has-text("Exclusive possession"), text=Exclusive possession');
    }
    if (orders.restraining_order) {
      await this.page.click('label:has-text("Restraining order"), text=Restraining order');
    }
    if (orders.enforcement) {
      await this.page.click('label:has-text("Enforcement"), text=Enforcement');
    }
    if (orders.other) {
      await this.page.click('label:has-text("Other relief"), text=Other relief');
    }
    
    await this.clickContinue();
  }

  /**
   * Handle orders sought for never lived together cases
   */
  async handleNeverTogetherOrders(orders) {
    await this.waitForQuestion('What orders are you seeking?');
    
    // Click on the label text to check/uncheck boxes since docassemble uses dynamic names
    if (orders.custody) await this.page.click('text=Child custody');
    if (orders.child_support) await this.page.click('text=Child support');
    if (orders.paternity) await this.page.click('text=Paternity');
    if (orders.restraining_order) await this.page.click('text=Restraining order');
    if (orders.other) await this.page.click('text=Other relief');
    
    await this.clickContinue();
  }

  /**
   * Handle divorce complexity question
   */
  async handleDivorceComplexity(complexity) {
    await this.waitForQuestion('Is your divorce contested or uncontested?');
    
    if (complexity === 'uncontested') {
      await this.page.locator(this.uncontestedButton).click();
    } else {
      await this.page.locator(this.contestedButton).click();
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Handle children involved question for simple divorce
   */
  async handleChildrenInvolved(hasChildren) {
    await this.waitForQuestion('Do you have children together?');
    
    if (hasChildren) {
      await this.page.locator(this.yesButton).click();
    } else {
      await this.page.locator(this.noButton).click();
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Handle financial situation questions
   */
  async handleFinancialSituation(financialData) {
    await this.waitForQuestion('What is your financial situation?');
    
    // Fill property value - use the currency input field
    await this.page.locator('input[type="text"]').first().fill(financialData.property_value.toString());
    
    // Use label clicking for radio buttons - more reliable than trying to click the radio directly
    // Support involved question
    if (financialData.support_involved) {
      await this.page.locator('label:has-text("Yes")').first().click();
    } else {
      await this.page.locator('label:has-text("No")').first().click();
    }
    
    // Business owner question - second set of Yes/No
    if (financialData.business_owner) {
      await this.page.locator('label:has-text("Yes")').nth(1).click();
    } else {
      await this.page.locator('label:has-text("No")').nth(1).click();
    }
    
    // Pension involved question - third set of Yes/No
    if (financialData.pension_involved) {
      await this.page.locator('label:has-text("Yes")').nth(2).click();
    } else {
      await this.page.locator('label:has-text("No")').nth(2).click();
    }
    
    await this.clickContinue();
  }

  /**
   * Handle recommendations screen
   */
  async handleRecommendations() {
    await this.waitForQuestion('Your Personalized Forms Package');
    await this.clickContinue();
  }

  /**
   * Verify we reach the final screen
   */
  async verifyFinalScreen(expectEmergency = false) {
    if (expectEmergency) {
      await this.waitForQuestion('Complete Case Assessment - EMERGENCY FILING REQUIRED');
    } else {
      await this.waitForQuestion('Ready to Start Your Family Law Case');
    }
  }

  /**
   * Get the list of recommended forms from the recommendations screen
   */
  async getRecommendedForms() {
    const forms = [];
    const formLinks = this.page.locator('a[href*="/interview?i=docassemble.webapp:ontario-family-law/form"]');
    const count = await formLinks.count();
    
    for (let i = 0; i < count; i++) {
      const formText = await formLinks.nth(i).textContent();
      forms.push(formText.trim());
    }
    
    return forms;
  }

  /**
   * Check if a specific form is recommended
   */
  async isFormRecommended(formName) {
    const formLink = this.page.locator(`a:has-text("${formName}")`);
    return await formLink.isVisible();
  }

  /**
   * Get the timeline text from recommendations
   */
  async getTimeline() {
    const timelineElement = this.page.locator('text=Estimated timeline:').locator('xpath=following-sibling::text()[1]');
    return await timelineElement.textContent();
  }

  /**
   * Get the court information from recommendations
   */
  async getCourt() {
    const courtElement = this.page.locator('text=File at:').locator('xpath=following-sibling::text()[1]');
    return await courtElement.textContent();
  }

  /**
   * Take a screenshot for debugging
   */
  async takeScreenshot(name) {
    await this.page.screenshot({ 
      path: `playwright/screenshots/${name}-${Date.now()}.png`,
      fullPage: true 
    });
  }

  /**
   * Check for any error messages on the page
   */
  async checkForErrors() {
    const errorElements = this.page.locator('.da-error, .alert-danger, .error');
    const errorCount = await errorElements.count();
    
    if (errorCount > 0) {
      const errors = [];
      for (let i = 0; i < errorCount; i++) {
        errors.push(await errorElements.nth(i).textContent());
      }
      throw new Error(`Found ${errorCount} error(s) on page: ${errors.join(', ')}`);
    }
  }

  /**
   * Wait for any pending network requests to complete
   */
  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(500); // Additional wait for docassemble
  }
  
  /**
   * Fill party information fields
   */
  async fillPartyInformation(partyType, partyData) {
    // Wait for party information screen
    const questionText = await this.page.locator(this.questionText).textContent();
    
    // Fill first name
    if (partyData.firstName) {
      await this.page.fill('input[name*="first_name"], input[name*="firstName"]', partyData.firstName);
    }
    
    // Fill last name
    if (partyData.lastName) {
      await this.page.fill('input[name*="last_name"], input[name*="lastName"]', partyData.lastName);
    }
    
    // Fill address fields
    if (partyData.address) {
      await this.page.fill('input[name*="address"], input[name*="street"]', partyData.address);
    }
    
    if (partyData.city) {
      await this.page.fill('input[name*="city"]', partyData.city);
    }
    
    if (partyData.province) {
      await this.page.selectOption('select[name*="province"]', partyData.province);
    }
    
    if (partyData.postalCode) {
      await this.page.fill('input[name*="postal"], input[name*="zip"]', partyData.postalCode);
    }
    
    // Fill contact information
    if (partyData.phone) {
      await this.page.fill('input[name*="phone"], input[type="tel"]', partyData.phone);
    }
    
    if (partyData.email) {
      await this.page.fill('input[name*="email"], input[type="email"]', partyData.email);
    }
    
    // Fill date of birth if present
    if (partyData.birthDate) {
      await this.page.fill('input[type="date"], input[name*="birth"]', partyData.birthDate);
    }
  }
  
  /**
   * Handle lawyer representation questions
   */
  async handleLawyerRepresentation(hasLawyer, lawyerData = null) {
    // Wait for lawyer question
    await this.waitForQuestionContaining(['Do you have a lawyer?', 'Are you represented by a lawyer?', 'lawyer']);
    
    if (hasLawyer) {
      await this.page.click('button:has-text("Yes"), input[value="Yes"]');
      await this.page.waitForLoadState('networkidle');
      
      // Fill lawyer information if provided
      if (lawyerData) {
        await this.fillLawyerInformation(lawyerData);
      }
    } else {
      await this.page.click('button:has-text("No"), input[value="No"], button:has-text("self-represented")');
      await this.page.waitForLoadState('networkidle');
    }
  }
  
  /**
   * Fill lawyer information
   */
  async fillLawyerInformation(lawyerData) {
    // Fill lawyer name
    if (lawyerData.firstName) {
      await this.page.fill('input[name*="lawyer"][name*="first"], input[name*="attorney"][name*="first"]', lawyerData.firstName);
    }
    
    if (lawyerData.lastName) {
      await this.page.fill('input[name*="lawyer"][name*="last"], input[name*="attorney"][name*="last"]', lawyerData.lastName);
    }
    
    // Fill law firm information
    if (lawyerData.firmName) {
      await this.page.fill('input[name*="firm"], input[name*="organization"]', lawyerData.firmName);
    }
    
    // Fill contact information
    if (lawyerData.phone) {
      await this.page.fill('input[name*="lawyer"][name*="phone"], input[name*="attorney"][name*="phone"]', lawyerData.phone);
    }
    
    if (lawyerData.email) {
      await this.page.fill('input[name*="lawyer"][name*="email"], input[name*="attorney"][name*="email"]', lawyerData.email);
    }
    
    // Fill address
    if (lawyerData.address) {
      await this.page.fill('input[name*="lawyer"][name*="address"], input[name*="attorney"][name*="address"]', lawyerData.address);
    }
  }
}

module.exports = { WizardPage };