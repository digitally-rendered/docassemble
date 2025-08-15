/**
 * Helper functions for handling docassemble interview quirks
 */

/**
 * Wait for docassemble to fully load a page
 * Docassemble can be slow and may update the DOM multiple times
 */
async function waitForDocassembleLoad(page) {
  // Wait for network to be idle
  await page.waitForLoadState('networkidle');
  
  // Additional wait for docassemble's JavaScript to finish
  await page.waitForTimeout(1000);
  
  // Check if still loading
  const spinner = await page.locator('.da-spinner').count();
  if (spinner > 0) {
    await page.waitForSelector('.da-spinner', { state: 'hidden', timeout: 10000 });
  }
}

/**
 * Check if the interview has crashed and extract error details
 */
async function checkForInterviewCrash(page) {
  const errorHeading = await page.locator('h1:has-text("Error")').count();
  
  if (errorHeading > 0) {
    let errorDetails = {
      crashed: true,
      message: '',
      type: 'unknown'
    };
    
    // Try to get the error message from blockquote
    const blockquote = await page.locator('blockquote').count();
    if (blockquote > 0) {
      errorDetails.message = await page.locator('blockquote').textContent();
      
      // Identify common error types
      if (errorDetails.message.includes('could not be looked up')) {
        errorDetails.type = 'undefined_variable';
        const match = errorDetails.message.match(/variable '([^']+)'/);
        if (match) {
          errorDetails.variable = match[1];
        }
      } else if (errorDetails.message.includes('SyntaxError')) {
        errorDetails.type = 'syntax_error';
      } else if (errorDetails.message.includes('indentation')) {
        errorDetails.type = 'indentation_error';
      }
    }
    
    return errorDetails;
  }
  
  return { crashed: false };
}

/**
 * Safely click a radio button by its label text
 * Handles docassemble's dynamic field names
 */
async function clickRadioByLabel(page, labelText, index = 0) {
  // Try to click the label directly
  const labels = page.locator(`label:has-text("${labelText}")`);
  const count = await labels.count();
  
  if (count > index) {
    await labels.nth(index).click();
    return true;
  }
  
  // Fallback: try to find the radio button near the text
  const radioNearText = page.locator(`input[type="radio"]:near(:text("${labelText}"))`);
  if (await radioNearText.count() > 0) {
    await radioNearText.first().click();
    return true;
  }
  
  return false;
}

/**
 * Safely fill a text input by its label
 */
async function fillInputByLabel(page, labelText, value) {
  // Try to find input by label association
  const label = page.locator(`label:has-text("${labelText}")`);
  if (await label.count() > 0) {
    const forAttr = await label.getAttribute('for');
    if (forAttr) {
      await page.locator(`#${forAttr}`).fill(value.toString());
      return true;
    }
  }
  
  // Fallback: find input near the label text
  const inputNearText = page.locator(`input[type="text"]:near(:text("${labelText}"))`);
  if (await inputNearText.count() > 0) {
    await inputNearText.first().fill(value.toString());
    return true;
  }
  
  return false;
}

/**
 * Click a checkbox by its label text
 */
async function clickCheckboxByLabel(page, labelText) {
  // Click on the text to toggle the checkbox
  // Docassemble usually makes the entire label clickable
  const labelElement = page.locator(`label:has-text("${labelText}")`);
  if (await labelElement.count() > 0) {
    await labelElement.first().click();
    return true;
  }
  
  // Fallback: click the text directly
  await page.click(`text="${labelText}"`);
  return true;
}

/**
 * Handle the financial situation form with improved selectors
 */
async function fillFinancialForm(page, financialData) {
  // Fill property value
  await page.locator('input[type="text"]').first().fill(financialData.property_value.toString());
  
  // Click radio buttons using improved label selection
  // Question 1: Support involved
  await clickRadioByLabel(page, financialData.support_involved ? 'Yes' : 'No', 0);
  
  // Question 2: Business owner
  await clickRadioByLabel(page, financialData.business_owner ? 'Yes' : 'No', 1);
  
  // Question 3: Pension involved
  await clickRadioByLabel(page, financialData.pension_involved ? 'Yes' : 'No', 2);
}

/**
 * Navigate safely with error checking
 */
async function safeNavigate(page, action) {
  // Perform the action
  await action();
  
  // Wait for page to load
  await waitForDocassembleLoad(page);
  
  // Check for crashes
  const crashInfo = await checkForInterviewCrash(page);
  if (crashInfo.crashed) {
    throw new Error(`Interview crashed: ${crashInfo.message}`);
  }
}

module.exports = {
  waitForDocassembleLoad,
  checkForInterviewCrash,
  clickRadioByLabel,
  fillInputByLabel,
  clickCheckboxByLabel,
  fillFinancialForm,
  safeNavigate
};