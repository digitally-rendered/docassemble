const { test, expect } = require('@playwright/test');
const { WizardPage } = require('../pages/WizardPage');

test.describe('Party Information Collection Flow', () => {
  let wizardPage;

  test.beforeEach(async ({ page }) => {
    wizardPage = new WizardPage(page);
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
  });

  test('should collect party information with role-neutral approach', async ({ page }) => {
    // Navigate through initial screens
    await wizardPage.page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(1000);
    
    // Handle emergency
    await wizardPage.page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // Handle MIP
    await wizardPage.page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Select relationship status
    await wizardPage.page.click('button:has-text("Married")');
    await page.waitForTimeout(1000);
    
    // Select orders sought (divorce)
    await wizardPage.page.click('text=Divorce');
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Handle divorce complexity
    await wizardPage.page.click('button:has-text("Uncontested - we agree on everything")');
    await page.waitForTimeout(1000);
    
    // Handle children question
    await wizardPage.page.click('button:has-text("No")');
    await page.waitForTimeout(1000);
    
    // Now we should get the role determination screen
    const roleContent = await page.content();
    expect(roleContent).toContain('Your Role in the Legal Proceeding');
    
    // Select role as applicant
    await wizardPage.page.click('button:has-text("I am starting a new case (Applicant)")');
    await page.waitForTimeout(1000);
    
    // Fill user information (applicant)
    const userInfoContent = await page.content();
    expect(userInfoContent).toContain('Your Information');
    
    // Fill out user party information
    await page.fill('input[name="user_party.name.first"]', 'John');
    await page.fill('input[name="user_party.name.last"]', 'Smith');
    await page.fill('input[name="user_party.birthdate"]', '01/01/1980');
    await page.fill('input[name="user_party.phone_number"]', '416-555-1234');
    await page.fill('input[name="user_party.email"]', 'john.smith@example.com');
    await page.fill('input[name="user_party.address.address"]', '123 Main Street');
    await page.fill('input[name="user_party.address.city"]', 'Toronto');
    await page.fill('input[name="user_party.address.postal_code"]', 'M5H 2N2');
    
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill other party information (respondent)
    const otherInfoContent = await page.content();
    expect(otherInfoContent).toContain('Other Party');
    
    await page.fill('input[name="other_party.name.first"]', 'Jane');
    await page.fill('input[name="other_party.name.last"]', 'Doe');
    await page.fill('input[name="other_party.phone_number"]', '416-555-5678');
    await page.fill('input[name="other_party.address.address"]', '456 Oak Avenue');
    await page.fill('input[name="other_party.address.city"]', 'Toronto');
    await page.fill('input[name="other_party.address.postal_code"]', 'M4W 1J5');
    
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Handle lawyer question for user
    await wizardPage.page.click('button:has-text("No, I am self-represented")');
    await page.waitForTimeout(1000);
    
    // Handle lawyer question for other party
    await wizardPage.page.click('button:has-text("I don\'t know")');
    await page.waitForTimeout(1000);
    
    // Fill court information
    const courtContent = await page.content();
    expect(courtContent).toContain('Court Information');
    
    await page.fill('input[name="court.location"]', 'Toronto');
    await page.fill('input[name="court.address.address"]', '393 University Avenue');
    
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // Verify we reached the recommendations
    const recommendationsContent = await page.content();
    expect(recommendationsContent).toContain('Your Personalized Forms Package');
    
    console.log('✅ Party information collection flow completed successfully');
  });

  test('should handle respondent role selection', async ({ page }) => {
    // Navigate through initial screens
    await wizardPage.page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(1000);
    
    // Handle emergency
    await wizardPage.page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // Handle MIP
    await wizardPage.page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Select relationship status
    await wizardPage.page.click('button:has-text("Common-law")');
    await page.waitForTimeout(1000);
    
    // Select orders sought
    await wizardPage.page.click('text=Child support');
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill financial form
    await page.locator('input[type="text"]').first().fill('30000');
    await page.locator('label:has-text("Yes")').first().click();
    await page.locator('label:has-text("No")').nth(1).click();
    await page.locator('label:has-text("No")').nth(2).click();
    await wizardPage.page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Now select role as respondent
    await wizardPage.page.click('button:has-text("I am responding to a case filed against me (Respondent)")');
    await page.waitForTimeout(1000);
    
    // Should get procedural position question
    const proceduralContent = await page.content();
    expect(proceduralContent).toContain('Current Procedural Position');
    
    await wizardPage.page.click('button:has-text("Responding to a motion/application (Responding Party)")');
    await page.waitForTimeout(1000);
    
    // Now user is respondent, so party labels should reflect that
    const userInfoContent = await page.content();
    expect(userInfoContent).toContain('Your Information');
    expect(userInfoContent).toContain('Respondent');
    
    console.log('✅ Respondent role selection handled correctly');
  });
});