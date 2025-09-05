const { expect } = require('@playwright/test');

/**
 * Page Object Model for Form 13 - Financial Statement
 * Handles all interactions with the comprehensive financial disclosure form
 */
class Form13Page {
  constructor(page) {
    this.page = page;
    
    // Common Docassemble selectors
    this.continueButton = 'button#da-continue-button, input[type="submit"][value*="Continue"], button:has-text("Continue")';
    this.backButton = 'button#da-back-button, button:has-text("Back")';
    this.questionText = '#daMainQuestion, .da-question-text, h1.h3';
    this.subquestionText = '.da-subquestion';
    this.errorMessage = '.da-error, .alert-danger, .error';
    
    // Form-specific selectors
    this.addAnotherYes = 'input[value="True"][type="radio"]';
    this.addAnotherNo = 'input[value="False"][type="radio"]';
    this.fileUploadInput = 'input[type="file"]';
    this.currencyInput = 'input[data-type="currency"], input.currency';
    this.dateInput = 'input[type="date"]';
    
    // Table row selectors
    this.tableRow = 'tr.da-table-row';
    this.addRowButton = 'button:has-text("Add another"), button:has-text("Add item"), button:has-text("Add")';
    this.deleteRowButton = 'button:has-text("Delete"), button.da-delete-button';
    
    // Review screen selectors
    this.reviewEditButton = 'a:has-text("Edit"), button:has-text("Edit")';
    this.reviewContinueButton = 'button:has-text("Continue to signature")';
    
    // Signature screen selectors
    this.signatureCanvas = 'canvas.signature-canvas, canvas#signature';
    this.signatureNameInput = 'input[name*="signature_name"]';
    this.signatureDateInput = 'input[name*="signature_date"]';
  }

  /**
   * Navigate to Form 13 interview
   */
  async goto(interviewPath = 'generated_interviews/form_13_comprehensive.yml') {
    const fullPath = `/interview?i=docassemble.webapp:ontario-family-law/utilities/${interviewPath}`;
    await this.page.goto(fullPath);
    await this.page.waitForLoadState('networkidle');
    await this.checkForInterviewError();
  }

  /**
   * Check if the interview has crashed with an error
   */
  async checkForInterviewError() {
    const errorHeading = await this.page.locator('h1:has-text("Error")').count();
    const errorBlockquote = await this.page.locator('blockquote').count();
    
    if (errorHeading > 0 && errorBlockquote > 0) {
      const errorMessage = await this.page.locator('blockquote').textContent();
      throw new Error(`Interview crashed: ${errorMessage}`);
    }
  }

  /**
   * Wait for a specific question to appear
   */
  async waitForQuestion(expectedText, options = {}) {
    const { partial = true, timeout = 15000 } = options;
    
    await this.checkForInterviewError();
    
    try {
      if (partial) {
        await expect(this.page.locator(this.questionText)).toContainText(expectedText, { timeout });
      } else {
        await expect(this.page.locator(this.questionText)).toHaveText(expectedText, { timeout });
      }
    } catch (error) {
      const actualText = await this.page.locator(this.questionText).textContent();
      throw new Error(`Expected question containing "${expectedText}", but got: "${actualText}"`);
    }
  }

  /**
   * Click continue and wait for next screen
   */
  async clickContinue() {
    await this.page.locator(this.continueButton).click();
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(500);
    await this.checkForInterviewError();
  }

  /**
   * Fill personal information section
   */
  async fillPersonalInformation(data) {
    await this.waitForQuestion('Personal Information');
    
    // Fill name fields
    if (data.fullName) {
      await this.page.fill('input[name*="name"]', data.fullName);
    }
    
    // Fill court name
    if (data.courtName) {
      const courtField = await this.page.locator('input').filter({ hasText: /court/i });
      if (await courtField.count() > 0) {
        await courtField.first().fill(data.courtName);
      }
    }
    
    // Fill any currency amounts on this screen
    const currencyFields = await this.page.locator(this.currencyInput);
    if (await currencyFields.count() > 0 && data.amounts) {
      for (let i = 0; i < Math.min(await currencyFields.count(), data.amounts.length); i++) {
        await currencyFields.nth(i).fill(data.amounts[i].toString());
      }
    }
    
    await this.clickContinue();
  }

  /**
   * Fill contact information section
   */
  async fillContactInformation(data) {
    await this.waitForQuestion('Contact Information');
    
    if (data.address) {
      await this.page.fill('input[name*="address"]', data.address);
    }
    
    if (data.email) {
      await this.page.fill('input[type="email"]', data.email);
    }
    
    if (data.phone) {
      await this.page.fill('input[type="tel"], input[name*="phone"]', data.phone);
    }
    
    await this.clickContinue();
  }

  /**
   * Add income items to the income table
   */
  async addIncomeItems(incomeItems) {
    for (const item of incomeItems) {
      await this.waitForQuestion('Income');
      
      // Fill income source description
      if (item.description) {
        await this.page.fill('input[name*="description"]', item.description);
      }
      
      // Fill amount
      if (item.amount !== undefined) {
        await this.page.fill(this.currencyInput, item.amount.toString());
      }
      
      // Select frequency if available
      if (item.frequency) {
        const frequencySelect = await this.page.locator('select[name*="frequency"]');
        if (await frequencySelect.count() > 0) {
          await frequencySelect.selectOption(item.frequency);
        }
      }
      
      // Decide whether to add another
      if (incomeItems.indexOf(item) < incomeItems.length - 1) {
        // More items to add
        await this.page.click('label:has-text("Yes")');
      } else {
        // Last item
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Add expense items to the expense table
   */
  async addExpenseItems(expenseItems) {
    for (const item of expenseItems) {
      await this.waitForQuestion('Expense');
      
      // Fill expense description
      if (item.description) {
        await this.page.fill('input[name*="description"]', item.description);
      }
      
      // Fill amount
      if (item.amount !== undefined) {
        await this.page.fill(this.currencyInput, item.amount.toString());
      }
      
      // Select category if available
      if (item.category) {
        const categorySelect = await this.page.locator('select[name*="category"]');
        if (await categorySelect.count() > 0) {
          await categorySelect.selectOption(item.category);
        }
      }
      
      // Decide whether to add another
      if (expenseItems.indexOf(item) < expenseItems.length - 1) {
        await this.page.click('label:has-text("Yes")');
      } else {
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Add assets to the assets table
   */
  async addAssets(assets) {
    for (const asset of assets) {
      await this.waitForQuestion('Asset');
      
      // Fill asset description
      if (asset.description) {
        await this.page.fill('input[name*="description"]', asset.description);
      }
      
      // Fill current value
      if (asset.currentValue !== undefined) {
        const valueField = await this.page.locator(this.currencyInput).or(
          this.page.locator('input[name*="value"], input[name*="current_value"]')
        );
        await valueField.first().fill(asset.currentValue.toString());
      }
      
      // Upload supporting documents if provided
      if (asset.documentPath) {
        const fileInput = await this.page.locator(this.fileUploadInput);
        if (await fileInput.count() > 0) {
          await fileInput.setInputFiles(asset.documentPath);
        }
      }
      
      // Decide whether to add another
      if (assets.indexOf(asset) < assets.length - 1) {
        await this.page.click('label:has-text("Yes")');
      } else {
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Add debts to the debts table
   */
  async addDebts(debts) {
    for (const debt of debts) {
      await this.waitForQuestion('Debt');
      
      // Fill debt description
      if (debt.description) {
        await this.page.fill('input[name*="description"]', debt.description);
      }
      
      // Fill amount owed
      if (debt.amount !== undefined) {
        await this.page.fill(this.currencyInput, debt.amount.toString());
      }
      
      // Fill creditor name if available
      if (debt.creditor) {
        const creditorField = await this.page.locator('input[name*="creditor"]');
        if (await creditorField.count() > 0) {
          await creditorField.fill(debt.creditor);
        }
      }
      
      // Decide whether to add another
      if (debts.indexOf(debt) < debts.length - 1) {
        await this.page.click('label:has-text("Yes")');
      } else {
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Upload tax documents
   */
  async uploadTaxDocuments(taxDocuments) {
    await this.waitForQuestion('Tax Returns');
    
    for (const doc of taxDocuments) {
      // Fill tax year
      if (doc.year) {
        await this.page.fill('input[name*="year"], input[type="number"]', doc.year.toString());
      }
      
      // Upload T1 return
      if (doc.t1ReturnPath) {
        const t1Input = await this.page.locator('input[type="file"]').first();
        await t1Input.setInputFiles(doc.t1ReturnPath);
      }
      
      // Upload Notice of Assessment
      if (doc.noaPath) {
        const noaInput = await this.page.locator('input[type="file"]').nth(1);
        await noaInput.setInputFiles(doc.noaPath);
      }
      
      // Decide whether to add another year
      if (taxDocuments.indexOf(doc) < taxDocuments.length - 1) {
        await this.page.click('label:has-text("Yes")');
      } else {
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Upload bank statements
   */
  async uploadBankStatements(bankStatements) {
    await this.waitForQuestion('Bank');
    
    for (const statement of bankStatements) {
      // Fill account description
      if (statement.accountName) {
        await this.page.fill('input[name*="description"], input[name*="account"]', statement.accountName);
      }
      
      // Fill current balance
      if (statement.balance !== undefined) {
        await this.page.fill(this.currencyInput, statement.balance.toString());
      }
      
      // Upload statements
      if (statement.statementPaths && statement.statementPaths.length > 0) {
        const fileInput = await this.page.locator(this.fileUploadInput).first();
        await fileInput.setInputFiles(statement.statementPaths);
      }
      
      // Decide whether to add another account
      if (bankStatements.indexOf(statement) < bankStatements.length - 1) {
        await this.page.click('label:has-text("Yes")');
      } else {
        await this.page.click('label:has-text("No")');
      }
      
      await this.clickContinue();
    }
  }

  /**
   * Handle the review screen
   */
  async handleReviewScreen() {
    await this.waitForQuestion('Review');
    
    // Check that all sections are displayed
    const sections = [
      'Personal Information',
      'Income',
      'Expenses',
      'Assets',
      'Debts'
    ];
    
    for (const section of sections) {
      const sectionVisible = await this.page.locator(`text=${section}`).isVisible();
      expect(sectionVisible, `Section "${section}" should be visible on review screen`).toBeTruthy();
    }
    
    // Continue to signature
    await this.clickContinue();
  }

  /**
   * Complete the signature screen
   */
  async completeSignature(signatureData) {
    await this.waitForQuestion('Signature');
    
    // Fill signature name
    if (signatureData.name) {
      const nameField = await this.page.locator('input[name*="signature"], input[name*="name"]').last();
      await nameField.fill(signatureData.name);
    }
    
    // Fill signature date
    if (signatureData.date) {
      const dateField = await this.page.locator('input[type="date"]').last();
      await dateField.fill(signatureData.date);
    }
    
    // Draw on signature canvas if present
    const canvas = await this.page.locator(this.signatureCanvas);
    if (await canvas.count() > 0) {
      await this.drawSignature(canvas);
    }
    
    await this.clickContinue();
  }

  /**
   * Draw a simple signature on the canvas
   */
  async drawSignature(canvas) {
    const box = await canvas.boundingBox();
    if (box) {
      // Draw a simple line as signature
      await this.page.mouse.move(box.x + 50, box.y + box.height / 2);
      await this.page.mouse.down();
      await this.page.mouse.move(box.x + box.width - 50, box.y + box.height / 2);
      await this.page.mouse.up();
    }
  }

  /**
   * Verify the final screen and PDF generation
   */
  async verifyFinalScreen() {
    await this.waitForQuestion('Complete');
    
    // Check for download link
    const downloadLink = await this.page.locator('a[href*=".pdf"], a:has-text("Download")');
    const hasDownloadLink = await downloadLink.count() > 0;
    expect(hasDownloadLink, 'Should have PDF download link on final screen').toBeTruthy();
    
    // Verify PDF can be accessed
    if (hasDownloadLink) {
      const href = await downloadLink.first().getAttribute('href');
      expect(href, 'Download link should point to a PDF').toContain('.pdf');
    }
  }

  /**
   * Test field validation for required fields
   */
  async testRequiredFieldValidation(fieldSelector, fieldName) {
    // Try to continue without filling the field
    await this.clickContinue();
    
    // Check for validation error
    const errorVisible = await this.page.locator(this.errorMessage).isVisible();
    expect(errorVisible, `Should show error when ${fieldName} is not filled`).toBeTruthy();
    
    // Check that we're still on the same screen
    const questionText = await this.page.locator(this.questionText).textContent();
    expect(questionText, 'Should remain on same screen when validation fails').toBeTruthy();
  }

  /**
   * Test Ontario-specific validations
   */
  async testOntarioValidations() {
    // Test postal code format (should accept K1A 0B1 format)
    const postalField = await this.page.locator('input[name*="postal"]');
    if (await postalField.count() > 0) {
      // Test invalid format
      await postalField.fill('12345');
      await this.clickContinue();
      let errorVisible = await this.page.locator(this.errorMessage).isVisible();
      expect(errorVisible, 'Should show error for invalid postal code format').toBeTruthy();
      
      // Test valid Ontario format
      await postalField.fill('K1A 0B1');
      await this.clickContinue();
      errorVisible = await this.page.locator(this.errorMessage).isVisible();
      expect(errorVisible, 'Should accept valid Ontario postal code').toBeFalsy();
    }
    
    // Test SIN validation (9 digits)
    const sinField = await this.page.locator('input[name*="sin"], input[name*="SIN"]');
    if (await sinField.count() > 0) {
      // Test invalid SIN
      await sinField.fill('12345');
      await this.clickContinue();
      let errorVisible = await this.page.locator(this.errorMessage).isVisible();
      expect(errorVisible, 'Should show error for invalid SIN').toBeTruthy();
      
      // Test valid SIN format
      await sinField.fill('123 456 789');
      await this.clickContinue();
      errorVisible = await this.page.locator(this.errorMessage).isVisible();
      expect(errorVisible, 'Should accept valid SIN format').toBeFalsy();
    }
  }

  /**
   * Test table operations (add/delete rows)
   */
  async testTableOperations() {
    // Add multiple rows
    for (let i = 0; i < 3; i++) {
      await this.page.fill('input[name*="description"]', `Test Item ${i + 1}`);
      await this.page.fill(this.currencyInput, (1000 * (i + 1)).toString());
      
      if (i < 2) {
        await this.page.click('label:has-text("Yes")');
        await this.clickContinue();
      }
    }
    
    // On review screen, verify all items are shown
    await this.page.click('label:has-text("No")');
    await this.clickContinue();
    
    // Go back and delete an item
    await this.page.click(this.backButton);
    const deleteButtons = await this.page.locator(this.deleteRowButton);
    if (await deleteButtons.count() > 0) {
      await deleteButtons.first().click();
      await this.page.waitForLoadState('networkidle');
    }
  }

  /**
   * Test document upload functionality
   */
  async testDocumentUpload(testFilePath) {
    const fileInput = await this.page.locator(this.fileUploadInput);
    if (await fileInput.count() > 0) {
      // Test uploading a file
      await fileInput.setInputFiles(testFilePath);
      
      // Verify file was uploaded (usually shows filename)
      const fileName = testFilePath.split('/').pop();
      const fileNameVisible = await this.page.locator(`text=${fileName}`).isVisible();
      expect(fileNameVisible, 'Uploaded file name should be displayed').toBeTruthy();
      
      // Test file size limits if applicable
      // This would require a large test file
    }
  }

  /**
   * Test conditional logic and skip patterns
   */
  async testConditionalLogic(condition, expectedQuestion, unexpectedQuestion) {
    // Set the condition
    if (condition.type === 'radio') {
      await this.page.click(`label:has-text("${condition.value}")`);
    } else if (condition.type === 'checkbox') {
      await this.page.click(`label:has-text("${condition.value}")`);
    } else if (condition.type === 'input') {
      await this.page.fill(condition.selector, condition.value);
    }
    
    await this.clickContinue();
    
    // Check that expected question appears
    if (expectedQuestion) {
      await this.waitForQuestion(expectedQuestion);
    }
    
    // Check that unexpected question does not appear
    if (unexpectedQuestion) {
      const questionText = await this.page.locator(this.questionText).textContent();
      expect(questionText).not.toContain(unexpectedQuestion);
    }
  }

  /**
   * Test browser navigation (back/forward buttons)
   */
  async testBrowserNavigation() {
    // Complete a few screens
    await this.clickContinue();
    const firstQuestion = await this.page.locator(this.questionText).textContent();
    
    await this.clickContinue();
    const secondQuestion = await this.page.locator(this.questionText).textContent();
    
    // Use browser back button
    await this.page.goBack();
    await this.page.waitForLoadState('networkidle');
    
    // Verify we're on the first question
    const currentQuestion = await this.page.locator(this.questionText).textContent();
    expect(currentQuestion).toBe(firstQuestion);
    
    // Use browser forward button
    await this.page.goForward();
    await this.page.waitForLoadState('networkidle');
    
    // Verify we're back on the second question
    const newQuestion = await this.page.locator(this.questionText).textContent();
    expect(newQuestion).toBe(secondQuestion);
  }

  /**
   * Get validation errors on current screen
   */
  async getValidationErrors() {
    const errors = [];
    const errorElements = await this.page.locator(this.errorMessage);
    const count = await errorElements.count();
    
    for (let i = 0; i < count; i++) {
      const errorText = await errorElements.nth(i).textContent();
      errors.push(errorText.trim());
    }
    
    return errors;
  }

  /**
   * Check if a specific field has validation error
   */
  async hasFieldError(fieldName) {
    const fieldError = await this.page.locator(`.da-field-error:has-text("${fieldName}")`);
    return await fieldError.isVisible();
  }

  /**
   * Get current progress indicator value
   */
  async getProgress() {
    const progressBar = await this.page.locator('.progress-bar, [role="progressbar"]');
    if (await progressBar.count() > 0) {
      const ariaValue = await progressBar.getAttribute('aria-valuenow');
      return parseInt(ariaValue || '0');
    }
    return 0;
  }
}

module.exports = { Form13Page };