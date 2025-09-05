const { expect } = require('@playwright/test');

/**
 * Base Page Object Model for Ontario Family Law Forms
 * Contains common functionality shared across all form types
 */
class BaseFamilyLawFormPage {
  constructor(page, formNumber) {
    this.page = page;
    this.formNumber = formNumber;
    
    // Common Docassemble selectors
    this.selectors = {
      // Navigation
      continueButton: 'button#da-continue-button, input[type="submit"][value*="Continue"], button:has-text("Continue")',
      backButton: 'button#da-back-button, button:has-text("Back")',
      exitButton: 'button:has-text("Exit"), a:has-text("Exit")',
      saveButton: 'button:has-text("Save"), button#da-save-button',
      
      // Question elements
      questionText: '#daMainQuestion, .da-question-text, h1.h3',
      subquestionText: '.da-subquestion',
      helpText: '.da-help-text, .help-block',
      progressBar: '.progress-bar, [role="progressbar"]',
      
      // Form inputs
      textInput: 'input[type="text"]',
      emailInput: 'input[type="email"]',
      phoneInput: 'input[type="tel"]',
      dateInput: 'input[type="date"]',
      currencyInput: 'input[data-type="currency"], input.currency',
      numberInput: 'input[type="number"]',
      textArea: 'textarea',
      selectDropdown: 'select',
      radioButton: 'input[type="radio"]',
      checkbox: 'input[type="checkbox"]',
      fileInput: 'input[type="file"]',
      
      // Validation and errors
      errorMessage: '.da-error, .alert-danger, .error, .da-field-error',
      warningMessage: '.alert-warning, .warning',
      successMessage: '.alert-success, .success',
      requiredField: '.da-required, [required]',
      
      // Tables
      tableRow: 'tr.da-table-row',
      addRowButton: 'button:has-text("Add another"), button:has-text("Add item"), button:has-text("Add")',
      deleteRowButton: 'button:has-text("Delete"), button.da-delete-button',
      editRowButton: 'button:has-text("Edit"), button.da-edit-button',
      
      // Review screen
      reviewSection: '.da-review-section',
      reviewEditButton: 'a:has-text("Edit"), button:has-text("Edit")',
      reviewContinueButton: 'button:has-text("Continue to signature")',
      
      // Signature
      signatureCanvas: 'canvas.signature-canvas, canvas#signature',
      signatureNameInput: 'input[name*="signature_name"]',
      signatureDateInput: 'input[name*="signature_date"]',
      signatureClearButton: 'button:has-text("Clear signature")',
      
      // Final screen
      downloadLink: 'a[href*=".pdf"], a:has-text("Download")',
      emailButton: 'button:has-text("Email")',
      printButton: 'button:has-text("Print")'
    };
    
    // Ontario-specific patterns
    this.ontarioPatterns = {
      postalCode: /^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z] \d[ABCEGHJ-NPRSTV-Z]\d$/,
      phoneNumber: /^(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$/,
      sin: /^\d{3}[-\s]?\d{3}[-\s]?\d{3}$/,
      lsoNumber: /^\d{5}[A-Z]$/,
      courtFileNumber: /^[A-Z]{1,3}-\d{2}-\d{4,6}$/
    };
    
    // Common court names in Ontario
    this.ontarioCourts = [
      'Superior Court of Justice',
      'Ontario Court of Justice',
      'Family Court',
      'Small Claims Court',
      'Divisional Court'
    ];
    
    // Common cities in Ontario
    this.ontarioCities = [
      'Toronto', 'Ottawa', 'Mississauga', 'Brampton', 'Hamilton',
      'London', 'Markham', 'Vaughan', 'Kitchener', 'Windsor',
      'Richmond Hill', 'Oakville', 'Burlington', 'Oshawa', 'Barrie'
    ];
  }

  /**
   * Navigate to the form interview
   */
  async goto(interviewPath) {
    const basePath = '/interview?i=docassemble.webapp:ontario-family-law/utilities/';
    const fullPath = interviewPath.startsWith('/') ? interviewPath : basePath + interviewPath;
    
    await this.page.goto(fullPath);
    await this.page.waitForLoadState('networkidle');
    await this.checkForInterviewError();
  }

  /**
   * Check if the interview has crashed with an error
   */
  async checkForInterviewError() {
    // Check for Docassemble error page
    const errorHeading = await this.page.locator('h1:has-text("Error")').count();
    const errorBlockquote = await this.page.locator('blockquote').count();
    
    if (errorHeading > 0 && errorBlockquote > 0) {
      const errorMessage = await this.page.locator('blockquote').textContent();
      const errorDetails = await this.page.textContent('body');
      
      // Take screenshot for debugging
      await this.takeDebugScreenshot('interview-error');
      
      throw new Error(`Interview crashed: ${errorMessage}\nDetails: ${errorDetails}`);
    }
    
    // Check for YAML syntax errors
    const yamlError = await this.page.locator('text=/YAML syntax error/i').count();
    if (yamlError > 0) {
      const errorText = await this.page.textContent('body');
      throw new Error(`YAML syntax error in interview: ${errorText}`);
    }
    
    // Check for undefined variable errors
    const undefinedError = await this.page.locator('text=/is not defined/i').count();
    if (undefinedError > 0) {
      const errorText = await this.page.textContent('body');
      throw new Error(`Undefined variable error: ${errorText}`);
    }
  }

  /**
   * Wait for a specific question to appear
   */
  async waitForQuestion(expectedText, options = {}) {
    const { partial = true, timeout = 15000, caseInsensitive = true } = options;
    
    await this.checkForInterviewError();
    
    try {
      const questionLocator = this.page.locator(this.selectors.questionText);
      
      if (partial) {
        if (caseInsensitive) {
          await expect(questionLocator).toContainText(expectedText, { 
            timeout, 
            ignoreCase: true 
          });
        } else {
          await expect(questionLocator).toContainText(expectedText, { timeout });
        }
      } else {
        await expect(questionLocator).toHaveText(expectedText, { timeout });
      }
    } catch (error) {
      const actualText = await this.page.locator(this.selectors.questionText).textContent();
      throw new Error(`Expected question containing "${expectedText}", but got: "${actualText}"`);
    }
  }

  /**
   * Click continue and wait for next screen
   */
  async clickContinue() {
    // Check if continue button is enabled
    const continueButton = await this.page.locator(this.selectors.continueButton).first();
    await expect(continueButton).toBeEnabled({ timeout: 5000 });
    
    await continueButton.click();
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(500); // Allow Docassemble to process
    await this.checkForInterviewError();
  }

  /**
   * Click back button
   */
  async clickBack() {
    await this.page.locator(this.selectors.backButton).click();
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(500);
  }

  /**
   * Fill a text input field
   */
  async fillTextField(selector, value) {
    const field = await this.page.locator(selector).first();
    await field.clear();
    await field.fill(value);
  }

  /**
   * Select an option from dropdown
   */
  async selectOption(selector, value) {
    await this.page.selectOption(selector, value);
  }

  /**
   * Click a radio button by label text
   */
  async selectRadioByLabel(labelText) {
    await this.page.click(`label:has-text("${labelText}")`);
  }

  /**
   * Click a checkbox by label text
   */
  async toggleCheckbox(labelText, checked = true) {
    const checkbox = await this.page.locator(`label:has-text("${labelText}")`);
    const isChecked = await checkbox.locator('input').isChecked();
    
    if (isChecked !== checked) {
      await checkbox.click();
    }
  }

  /**
   * Upload a file
   */
  async uploadFile(filePath) {
    const fileInput = await this.page.locator(this.selectors.fileInput).first();
    await fileInput.setInputFiles(filePath);
  }

  /**
   * Validate Ontario postal code format
   */
  validatePostalCode(postalCode) {
    return this.ontarioPatterns.postalCode.test(postalCode);
  }

  /**
   * Validate Ontario phone number format
   */
  validatePhoneNumber(phoneNumber) {
    return this.ontarioPatterns.phoneNumber.test(phoneNumber);
  }

  /**
   * Validate SIN format
   */
  validateSIN(sin) {
    return this.ontarioPatterns.sin.test(sin);
  }

  /**
   * Validate LSO number format
   */
  validateLSONumber(lsoNumber) {
    return this.ontarioPatterns.lsoNumber.test(lsoNumber);
  }

  /**
   * Get validation errors on current screen
   */
  async getValidationErrors() {
    const errors = [];
    const errorElements = await this.page.locator(this.selectors.errorMessage);
    const count = await errorElements.count();
    
    for (let i = 0; i < count; i++) {
      const errorText = await errorElements.nth(i).textContent();
      if (errorText && errorText.trim()) {
        errors.push(errorText.trim());
      }
    }
    
    return errors;
  }

  /**
   * Check if field has validation error
   */
  async hasFieldError(fieldName) {
    const fieldError = await this.page.locator(
      `.da-field-error:has-text("${fieldName}"), .error:has-text("${fieldName}")`
    );
    return await fieldError.isVisible();
  }

  /**
   * Get current progress percentage
   */
  async getProgress() {
    const progressBar = await this.page.locator(this.selectors.progressBar);
    if (await progressBar.count() > 0) {
      const ariaValue = await progressBar.getAttribute('aria-valuenow');
      const style = await progressBar.getAttribute('style');
      
      if (ariaValue) {
        return parseInt(ariaValue);
      } else if (style && style.includes('width')) {
        const match = style.match(/width:\s*(\d+)%/);
        return match ? parseInt(match[1]) : 0;
      }
    }
    return 0;
  }

  /**
   * Take a screenshot for debugging
   */
  async takeDebugScreenshot(name) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${this.formNumber}_${name}_${timestamp}.png`;
    
    await this.page.screenshot({ 
      path: `playwright/screenshots/${fileName}`,
      fullPage: true 
    });
    
    console.log(`Screenshot saved: ${fileName}`);
  }

  /**
   * Wait for network to be idle
   */
  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(1000); // Extra wait for Docassemble
  }

  /**
   * Check if we're on a specific screen by checking question text
   */
  async isOnScreen(questionText) {
    try {
      const question = await this.page.locator(this.selectors.questionText).textContent();
      return question.toLowerCase().includes(questionText.toLowerCase());
    } catch {
      return false;
    }
  }

  /**
   * Get the current question text
   */
  async getCurrentQuestion() {
    return await this.page.locator(this.selectors.questionText).textContent();
  }

  /**
   * Get the current subquestion text
   */
  async getCurrentSubquestion() {
    const subquestion = await this.page.locator(this.selectors.subquestionText);
    if (await subquestion.count() > 0) {
      return await subquestion.textContent();
    }
    return '';
  }

  /**
   * Save the current state (if save button is available)
   */
  async saveProgress() {
    const saveButton = await this.page.locator(this.selectors.saveButton);
    if (await saveButton.isVisible()) {
      await saveButton.click();
      await this.page.waitForLoadState('networkidle');
      
      // Check for save confirmation
      const successMessage = await this.page.locator(this.selectors.successMessage);
      if (await successMessage.count() > 0) {
        console.log('Progress saved successfully');
      }
    }
  }

  /**
   * Handle session timeout by refreshing
   */
  async handleSessionTimeout() {
    const sessionError = await this.page.locator('text=/session.*expired/i');
    if (await sessionError.count() > 0) {
      console.log('Session expired, refreshing page...');
      await this.page.reload();
      await this.page.waitForLoadState('networkidle');
    }
  }

  /**
   * Test field with invalid input and verify error
   */
  async testInvalidInput(fieldSelector, invalidValue, expectedError) {
    await this.fillTextField(fieldSelector, invalidValue);
    await this.clickContinue();
    
    const errors = await this.getValidationErrors();
    const hasExpectedError = errors.some(error => 
      error.toLowerCase().includes(expectedError.toLowerCase())
    );
    
    expect(hasExpectedError, 
      `Expected error containing "${expectedError}" for invalid input "${invalidValue}"`
    ).toBeTruthy();
    
    // Clear the field for next test
    await this.fillTextField(fieldSelector, '');
  }

  /**
   * Test required field validation
   */
  async testRequiredField(fieldSelector, fieldName) {
    // Leave field empty and try to continue
    await this.fillTextField(fieldSelector, '');
    await this.clickContinue();
    
    // Should show error and stay on same screen
    const errors = await this.getValidationErrors();
    expect(errors.length, `Should show error for empty required field: ${fieldName}`).toBeGreaterThan(0);
    
    const currentQuestion = await this.getCurrentQuestion();
    expect(currentQuestion, 'Should remain on same screen when validation fails').toBeTruthy();
  }

  /**
   * Fill standard contact information fields
   */
  async fillContactInfo(contactData) {
    if (contactData.address) {
      await this.fillTextField('input[name*="address"]', contactData.address);
    }
    
    if (contactData.city) {
      await this.fillTextField('input[name*="city"]', contactData.city);
    }
    
    if (contactData.province) {
      const provinceSelect = await this.page.locator('select[name*="province"]');
      if (await provinceSelect.count() > 0) {
        await this.selectOption('select[name*="province"]', contactData.province);
      } else {
        await this.fillTextField('input[name*="province"]', contactData.province);
      }
    }
    
    if (contactData.postalCode) {
      await this.fillTextField('input[name*="postal"]', contactData.postalCode);
    }
    
    if (contactData.email) {
      await this.fillTextField(this.selectors.emailInput, contactData.email);
    }
    
    if (contactData.phone) {
      await this.fillTextField(this.selectors.phoneInput, contactData.phone);
    }
  }

  /**
   * Draw a simple signature on canvas
   */
  async drawSignature() {
    const canvas = await this.page.locator(this.selectors.signatureCanvas).first();
    const box = await canvas.boundingBox();
    
    if (box) {
      // Draw a simple signature line
      const startX = box.x + 50;
      const startY = box.y + box.height / 2;
      const endX = box.x + box.width - 50;
      const endY = box.y + box.height / 2;
      
      await this.page.mouse.move(startX, startY);
      await this.page.mouse.down();
      
      // Draw a wavy line for more realistic signature
      for (let i = 0; i < 5; i++) {
        const x = startX + (endX - startX) * (i / 4);
        const y = startY + (i % 2 === 0 ? -10 : 10);
        await this.page.mouse.move(x, y);
      }
      
      await this.page.mouse.move(endX, endY);
      await this.page.mouse.up();
    }
  }

  /**
   * Complete signature screen
   */
  async completeSignature(signatureData) {
    await this.waitForQuestion('Signature');
    
    if (signatureData.name) {
      const nameField = await this.page.locator(this.selectors.signatureNameInput);
      if (await nameField.count() > 0) {
        await this.fillTextField(this.selectors.signatureNameInput, signatureData.name);
      }
    }
    
    if (signatureData.date) {
      const dateField = await this.page.locator(this.selectors.signatureDateInput);
      if (await dateField.count() > 0) {
        await this.fillTextField(this.selectors.signatureDateInput, signatureData.date);
      }
    }
    
    // Draw signature on canvas if present
    const canvas = await this.page.locator(this.selectors.signatureCanvas);
    if (await canvas.count() > 0) {
      await this.drawSignature();
    }
    
    await this.clickContinue();
  }

  /**
   * Verify PDF generation on final screen
   */
  async verifyPDFGeneration() {
    // Wait for final screen
    await this.waitForQuestion('Complete', { partial: true });
    
    // Check for download link
    const downloadLink = await this.page.locator(this.selectors.downloadLink);
    const hasDownloadLink = await downloadLink.count() > 0;
    
    expect(hasDownloadLink, 'Should have PDF download link on final screen').toBeTruthy();
    
    if (hasDownloadLink) {
      const href = await downloadLink.first().getAttribute('href');
      expect(href, 'Download link should point to a PDF').toMatch(/\.pdf/i);
      
      // Verify the link is not broken
      const response = await this.page.request.head(href);
      expect(response.status(), 'PDF link should be accessible').toBe(200);
    }
    
    return hasDownloadLink;
  }

  /**
   * Measure page load performance
   */
  async measurePageLoadTime() {
    const startTime = Date.now();
    await this.clickContinue();
    const loadTime = Date.now() - startTime;
    
    console.log(`Page load time: ${loadTime}ms`);
    return loadTime;
  }

  /**
   * Test browser navigation (back/forward)
   */
  async testBrowserNavigation() {
    // Record current question
    const firstQuestion = await this.getCurrentQuestion();
    
    // Move forward
    await this.clickContinue();
    const secondQuestion = await this.getCurrentQuestion();
    
    // Use browser back
    await this.page.goBack();
    await this.waitForNetworkIdle();
    
    const backQuestion = await this.getCurrentQuestion();
    expect(backQuestion).toBe(firstQuestion);
    
    // Use browser forward
    await this.page.goForward();
    await this.waitForNetworkIdle();
    
    const forwardQuestion = await this.getCurrentQuestion();
    expect(forwardQuestion).toBe(secondQuestion);
  }
}

module.exports = { BaseFamilyLawFormPage };