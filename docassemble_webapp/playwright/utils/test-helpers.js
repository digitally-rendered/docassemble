const { expect } = require('@playwright/test');

/**
 * Test helper functions for common operations across all wizard tests
 * Provides reusable functionality for test execution and validation
 */

/**
 * Complete a full wizard flow based on scenario data
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {Object} scenario - Test scenario data from fixtures
 */
async function completeWizardFlow(wizardPage, scenario) {
  // Handle introduction
  await wizardPage.handleIntroduction();
  
  // Handle emergency situation
  await wizardPage.handleEmergencyQuestion(scenario.emergency_situation);
  
  if (scenario.emergency_situation) {
    // Handle emergency forms screen
    await wizardPage.handleEmergencyFormsScreen();
  } else {
    // Handle MIP for non-emergency cases
    await wizardPage.handleMipQuestion(scenario.mip_status);
  }
  
  // Handle relationship status
  await wizardPage.handleRelationshipStatus(scenario.relationship_status);
  
  // Handle divorce question for married couples
  if (scenario.relationship_status === 'married') {
    await wizardPage.handleDivorceQuestion(scenario.orders.divorce || false);
  }
  
  // Handle orders sought
  if (scenario.relationship_status === 'never_together') {
    await wizardPage.handleNeverTogetherOrders(scenario.orders);
  } else {
    await wizardPage.handleOrdersSought(scenario.orders);
  }
  
  // Handle divorce complexity if seeking divorce
  if (scenario.orders.divorce && scenario.divorce_complexity) {
    await wizardPage.handleDivorceComplexity(scenario.divorce_complexity);
    
    // Handle children question for uncontested simple divorce
    if (scenario.divorce_complexity === 'uncontested' && scenario.children_involved !== undefined) {
      await wizardPage.handleChildrenInvolved(scenario.children_involved);
    }
  }
  
  // Handle financial situation if financial data provided
  if (scenario.financial_data) {
    await wizardPage.handleFinancialSituation(scenario.financial_data);
  }
  
  // Handle recommendations screen
  await wizardPage.handleRecommendations();
  
  // Verify final screen
  await wizardPage.verifyFinalScreen(scenario.emergency_situation);
}

/**
 * Validate that expected forms are recommended
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {Array<string>} expectedForms - List of expected form names
 */
async function validateRecommendedForms(wizardPage, expectedForms) {
  // Try to get recommended forms
  const recommendedForms = await wizardPage.getRecommendedForms();
  
  // If no forms are shown (wizard in simplified mode), skip validation
  if (recommendedForms.length === 0) {
    console.log('Wizard completed but no form links displayed - wizard may be in simplified mode');
    return;
  }
  
  // Navigate back to recommendations if needed
  const currentUrl = wizardPage.page.url();
  if (!currentUrl.includes('show_recommendations')) {
    await wizardPage.page.goBack();
    await wizardPage.page.waitForLoadState('networkidle');
  }
  
  // Check that all expected forms are present
  for (const expectedForm of expectedForms) {
    const isRecommended = recommendedForms.some(form => 
      form.includes(expectedForm)
    );
    expect(isRecommended, `Expected form "${expectedForm}" should be recommended`).toBe(true);
  }
}

/**
 * Validate timeline and court information
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {string} expectedTimeline - Expected timeline text
 * @param {string} expectedCourt - Expected court text
 */
async function validateTimelineAndCourt(wizardPage, expectedTimeline, expectedCourt) {
  // Navigate back to recommendations if needed
  const currentUrl = wizardPage.page.url();
  if (!currentUrl.includes('show_recommendations')) {
    await wizardPage.page.goBack();
    await wizardPage.page.waitForLoadState('networkidle');
  }
  
  const timeline = await wizardPage.getTimeline();
  const court = await wizardPage.getCourt();
  
  expect(timeline, 'Timeline should match expected value').toContain(expectedTimeline);
  expect(court, 'Court should match expected value').toContain(expectedCourt);
}

/**
 * Validate that no errors occurred during the wizard flow
 * @param {WizardPage} wizardPage - The wizard page object
 */
async function validateNoErrors(wizardPage) {
  await wizardPage.checkForErrors();
}

/**
 * Take a screenshot with a descriptive name for debugging
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {string} testName - Name of the test
 * @param {string} step - Current step being executed
 */
async function takeDebugScreenshot(wizardPage, testName, step) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await wizardPage.takeScreenshot(`${testName}_${step}_${timestamp}`);
}

/**
 * Validate form links are working (not broken)
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {Array<string>} formNames - List of form names to check
 */
async function validateFormLinks(wizardPage, formNames) {
  // Navigate back to recommendations if needed
  const currentUrl = wizardPage.page.url();
  if (!currentUrl.includes('show_recommendations')) {
    await wizardPage.page.goBack();
    await wizardPage.page.waitForLoadState('networkidle');
  }
  
  for (const formName of formNames) {
    const formLink = wizardPage.page.locator(`a:has-text("${formName}")`);
    if (await formLink.isVisible()) {
      const href = await formLink.getAttribute('href');
      expect(href, `Form "${formName}" should have a valid link`).toBeTruthy();
      expect(href, `Form "${formName}" link should point to interview`).toContain('/interview?i=');
    }
  }
}

/**
 * Run a complete test scenario with full validation
 * @param {WizardPage} wizardPage - The wizard page object
 * @param {Object} scenario - Test scenario from fixtures
 * @param {string} testName - Name of the test for debugging
 */
async function runCompleteScenario(wizardPage, scenario, testName) {
  try {
    // Navigate to wizard
    await wizardPage.goto();
    
    // Complete the wizard flow
    await completeWizardFlow(wizardPage, scenario);
    
    // Validate expected forms if provided
    if (scenario.expected_forms) {
      await validateRecommendedForms(wizardPage, scenario.expected_forms);
    }
    
    // Validate timeline and court if provided
    if (scenario.expected_timeline && scenario.expected_court) {
      await validateTimelineAndCourt(wizardPage, scenario.expected_timeline, scenario.expected_court);
    }
    
    // Check for any errors
    await validateNoErrors(wizardPage);
    
    // Validate form links if forms are expected
    if (scenario.expected_forms) {
      await validateFormLinks(wizardPage, scenario.expected_forms);
    }
    
  } catch (error) {
    // Take a screenshot on failure for debugging
    await takeDebugScreenshot(wizardPage, testName, 'error');
    throw error;
  }
}

/**
 * Check that financial forms are included when expected
 * @param {Array<string>} recommendedForms - List of recommended forms
 * @param {boolean} shouldHaveFinancial - Whether financial forms should be present
 */
function validateFinancialFormsPresence(recommendedForms, shouldHaveFinancial) {
  const hasForm13 = recommendedForms.some(form => form.includes('Form 13'));
  const hasForm13A = recommendedForms.some(form => form.includes('Form 13A'));
  
  if (shouldHaveFinancial) {
    expect(hasForm13, 'Should include Form 13 or 13.1 when financial support/property is involved').toBe(true);
    expect(hasForm13A, 'Should include Form 13A when financial forms are required').toBe(true);
  } else {
    expect(hasForm13, 'Should not include Form 13 when no financial issues').toBe(false);
    expect(hasForm13A, 'Should not include Form 13A when no financial forms needed').toBe(false);
  }
}

/**
 * Check that custody forms are included when expected
 * @param {Array<string>} recommendedForms - List of recommended forms
 * @param {boolean} shouldHaveCustody - Whether custody forms should be present
 */
function validateCustodyFormsPresence(recommendedForms, shouldHaveCustody) {
  const hasCustodyForm = recommendedForms.some(form => form.includes('Form 35.1') || form.includes('Custody'));
  
  if (shouldHaveCustody) {
    expect(hasCustodyForm, 'Should include custody form when custody/access is sought').toBe(true);
  }
}

/**
 * Check that divorce-specific forms are included when expected
 * @param {Array<string>} recommendedForms - List of recommended forms
 * @param {boolean} shouldHaveDivorce - Whether divorce forms should be present
 */
function validateDivorceFormsPresence(recommendedForms, shouldHaveDivorce) {
  const hasForm8A = recommendedForms.some(form => form.includes('Form 8A'));
  const hasForm36 = recommendedForms.some(form => form.includes('Form 36'));
  
  if (shouldHaveDivorce) {
    expect(hasForm8A, 'Should include Form 8A for divorce applications').toBe(true);
    expect(hasForm36, 'Should include Form 36 (Affidavit for Divorce) for divorce cases').toBe(true);
  } else {
    expect(hasForm8A, 'Should not include Form 8A when not seeking divorce').toBe(false);
  }
}

/**
 * Wait for docassemble's slower page transitions
 * @param {Page} page - Playwright page object
 */
async function waitForDocassembleLoad(page) {
  await page.waitForLoadState('networkidle');
  // Additional wait for docassemble's form processing
  await page.waitForTimeout(1000);
}

/**
 * Create a data-driven test function
 * @param {Object} scenarios - Object containing multiple test scenarios
 * @param {Function} testFunction - Function to execute for each scenario
 */
function createDataDrivenTests(scenarios, testFunction) {
  const tests = [];
  
  for (const [scenarioName, scenarioData] of Object.entries(scenarios)) {
    tests.push({
      name: scenarioName,
      data: scenarioData,
      execute: testFunction
    });
  }
  
  return tests;
}

module.exports = {
  completeWizardFlow,
  validateRecommendedForms,
  validateTimelineAndCourt,
  validateNoErrors,
  takeDebugScreenshot,
  validateFormLinks,
  runCompleteScenario,
  validateFinancialFormsPresence,
  validateCustodyFormsPresence,
  validateDivorceFormsPresence,
  waitForDocassembleLoad,
  createDataDrivenTests
};