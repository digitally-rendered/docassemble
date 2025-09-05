import { test, expect, Page } from '@playwright/test';

// Helper function to start the interview
async function startInterview(page: Page) {
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
  await page.getByRole('button', { name: /Continue/i }).click();
}

// Helper to fill user info
async function fillUserInfo(page: Page, data: any = {}) {
  await page.fill('input[name*=".name.first"]', data.firstName || 'John');
  await page.fill('input[name*=".name.last"]', data.lastName || 'Smith');
  await page.fill('input[name*="birthdate"]', data.birthdate || '01/01/1980');
  if (data.alsoKnownAs) {
    await page.fill('input[name*="also_known_as"]', data.alsoKnownAs);
  }
  await page.getByRole('button', { name: /Continue/i }).click();
}

// Helper to fill contact info
async function fillContactInfo(page: Page, data: any = {}) {
  await page.fill('input[name*="address.address"]', data.address || '123 Main Street');
  if (data.unit) {
    await page.fill('input[name*="address.unit"]', data.unit);
  }
  await page.fill('input[name*="address.city"]', data.city || 'Toronto');
  await page.fill('input[name*="address.postal_code"]', data.postalCode || 'M5H 2N2');
  await page.fill('input[name*="phone_number"]', data.phone || '416-555-1234');
  if (data.email) {
    await page.fill('input[name*="email"]', data.email);
  }
  await page.getByRole('button', { name: /Continue/i }).click();
}

// ============================================================================
// TEST SUITE 1: EMERGENCY FLOW VARIATIONS
// ============================================================================

test.describe('Emergency Flow Paths', () => {
  test('Emergency situation - continues to MIP after warning', async ({ page }) => {
    await startInterview(page);
    
    // Select emergency
    await expect(page.locator('#daMainQuestion')).toContainText('Is this an emergency');
    await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
    
    // Should show emergency warning
    await expect(page.locator('#daMainQuestion')).toContainText('URGENT: Emergency Filing Required');
    await expect(page.locator('body')).toContainText('Form 8 - Application');
    await expect(page.locator('body')).toContainText('Form 14B - Notice of Motion');
    await expect(page.locator('body')).toContainText('911');
    await expect(page.locator('body')).toContainText('1-866-863-0511');
    
    // Continue past emergency warning
    await page.getByRole('button', { name: /Continue.*understand/i }).click();
    
    // Should proceed to MIP
    await expect(page.locator('#daMainQuestion')).toContainText('Mandatory Information Program');
  });

  test('No emergency - proceeds directly to MIP', async ({ page }) => {
    await startInterview(page);
    
    // Select no emergency
    await expect(page.locator('#daMainQuestion')).toContainText('Is this an emergency');
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // Should go directly to MIP without warning
    await expect(page.locator('#daMainQuestion')).toContainText('Mandatory Information Program');
    
    // Should not have seen emergency warning
    await expect(page.locator('body')).not.toContainText('URGENT: Emergency Filing Required');
  });
});

// ============================================================================
// TEST SUITE 2: MIP STATUS VARIATIONS
// ============================================================================

test.describe('MIP Status Paths', () => {
  test('MIP completed - proceeds to relationship', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // Select MIP completed
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    
    // Should proceed directly to relationship status
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  });

  test('MIP not completed - shows information then continues', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // Select MIP not completed
    await page.getByRole('button', { name: /No, I need to attend/i }).click();
    
    // Should show MIP registration info
    await expect(page.locator('#daMainQuestion')).toContainText('MIP Registration Required');
    await expect(page.locator('body')).toContainText('must attend MIP before filing');
    await expect(page.locator('body')).toContainText('Contact your local courthouse');
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to relationship status
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  });

  test('MIP unsure - shows information then continues', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // Select unsure
    await page.getByRole('button', { name: /Not sure/i }).click();
    
    // Should show MIP info
    await expect(page.locator('#daMainQuestion')).toContainText('MIP Registration Required');
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to relationship
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  });

  test('Emergency defer MIP - special message', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
    await page.getByRole('button', { name: /Continue.*understand/i }).click();
    
    // Select emergency defer
    await page.getByRole('button', { name: /Emergency - will complete after/i }).click();
    
    // Should show emergency defer message
    await expect(page.locator('#daMainQuestion')).toContainText('MIP Registration Required');
    await expect(page.locator('body')).toContainText('emergency situation');
    await expect(page.locator('body')).toContainText('must attend as soon as possible');
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to relationship
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  });
});

// ============================================================================
// TEST SUITE 3: RELATIONSHIP STATUS PATHS
// ============================================================================

test.describe('Relationship Status Paths', () => {
  async function navigateToRelationship(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  }

  test('Married - shows divorce option', async ({ page }) => {
    await navigateToRelationship(page);
    
    // Select married
    await page.getByRole('button', { name: /^Married$/i }).click();
    
    // Should show orders page with divorce option
    await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
    await expect(page.locator('body')).toContainText('Divorce');
    
    // Divorce should be visible for married couples
    const divorceField = page.locator('label:has-text("Divorce")');
    await expect(divorceField).toBeVisible();
  });

  test('Common-law - no divorce option', async ({ page }) => {
    await navigateToRelationship(page);
    
    // Select common-law
    await page.getByRole('button', { name: /Common-law/i }).click();
    
    // Should show orders page
    await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
    
    // Divorce should NOT be visible for common-law
    const divorceField = page.locator('label:has-text("Divorce")');
    await expect(divorceField).not.toBeVisible();
    
    // But should show other options
    await expect(page.locator('body')).toContainText('Child custody');
    await expect(page.locator('body')).toContainText('Child support');
    await expect(page.locator('body')).toContainText('Spousal support');
  });

  test('Never together - limited options', async ({ page }) => {
    await navigateToRelationship(page);
    
    // Select never together
    await page.getByRole('button', { name: /Never lived together/i }).click();
    
    // Should show orders page
    await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
    
    // Should show child-related and paternity options
    await expect(page.locator('body')).toContainText('Child custody');
    await expect(page.locator('body')).toContainText('Child support');
    await expect(page.locator('body')).toContainText('Paternity/parentage');
    
    // Should NOT show spousal support or property for never together
    const spousalField = page.locator('label:has-text("Spousal support")');
    await expect(spousalField).not.toBeVisible();
    const propertyField = page.locator('label:has-text("Property division")');
    await expect(propertyField).not.toBeVisible();
  });

  test('Separated - shows all options except divorce', async ({ page }) => {
    await navigateToRelationship(page);
    
    // Select separated
    await page.getByRole('button', { name: /^Separated$/i }).click();
    
    // Should show orders page
    await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
    
    // Should show most options but not divorce
    await expect(page.locator('body')).toContainText('Child custody');
    await expect(page.locator('body')).toContainText('Child support');
    
    // Divorce should not be visible for separated (not married)
    const divorceField = page.locator('label:has-text("Divorce")');
    await expect(divorceField).not.toBeVisible();
  });
});

// ============================================================================
// TEST SUITE 4: FINANCIAL FORMS LOGIC
// ============================================================================

test.describe('Financial Forms Logic', () => {
  async function navigateToOrders(page: Page, relationship: string = 'married') {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    
    if (relationship === 'married') {
      await page.getByRole('button', { name: /^Married$/i }).click();
    } else if (relationship === 'common-law') {
      await page.getByRole('button', { name: /Common-law/i }).click();
    } else {
      await page.getByRole('button', { name: /Never lived together/i }).click();
    }
  }

  test('Selecting support triggers financial questions', async ({ page }) => {
    await navigateToOrders(page, 'married');
    
    // Select child support
    await page.getByLabel(/Child support/).check();
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show financial information page
    await expect(page.locator('#daMainQuestion')).toContainText('Financial Information');
    await expect(page.locator('body')).toContainText('claiming support');
    await expect(page.locator('body')).toContainText('own a business');
    await expect(page.locator('body')).toContainText('investments');
  });

  test('Selecting property triggers financial questions', async ({ page }) => {
    await navigateToOrders(page, 'married');
    
    // Select property division
    await page.getByLabel(/Property division/).check();
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show financial information page
    await expect(page.locator('#daMainQuestion')).toContainText('Financial Information');
  });

  test('No financial orders skips financial questions', async ({ page }) => {
    await navigateToOrders(page, 'married');
    
    // Select only custody (no financial implications)
    await page.getByLabel(/Child custody/).check();
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should skip financial and go to personal info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Personal Information');
  });

  test('Spousal support triggers financial questions', async ({ page }) => {
    await navigateToOrders(page, 'common-law');
    
    // Select spousal support
    await page.getByLabel(/Spousal support/).check();
    
    // Continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show financial information page
    await expect(page.locator('#daMainQuestion')).toContainText('Financial Information');
  });
});

// ============================================================================
// TEST SUITE 5: LAWYER PRESENCE VARIATIONS
// ============================================================================

test.describe('Lawyer Representation Paths', () => {
  async function navigateToLawyerQuestion(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip orders
    
    // Fill user info
    await fillUserInfo(page);
    await fillContactInfo(page);
  }

  test('User has lawyer - collects lawyer details', async ({ page }) => {
    await navigateToLawyerQuestion(page);
    
    // Say yes to lawyer
    await page.getByRole('button', { name: /^Yes$/i }).click();
    
    // Should show lawyer info page
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Information');
    
    // Fill lawyer info
    await page.fill('input[name*="name.text"]', 'Jane Attorney');
    await page.fill('input[name*="firm_name"]', 'Smith & Associates');
    await page.fill('input[name*="lsuc_number"]', 'L12345');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show lawyer contact page
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Contact Information');
    
    // Fill lawyer contact
    await page.fill('input[name*="address.address"]', '100 Bay Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5J 2N8');
    await page.fill('input[name*="phone_number"]', '416-555-5555');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to other party
    await expect(page.locator('#daMainQuestion')).toContainText('Other Party Information');
  });

  test('User has no lawyer - skips lawyer pages', async ({ page }) => {
    await navigateToLawyerQuestion(page);
    
    // Say no to lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Should skip lawyer pages and go to other party
    await expect(page.locator('#daMainQuestion')).toContainText('Other Party Information');
  });

  test('Opposing party lawyer unknown', async ({ page }) => {
    await navigateToLawyerQuestion(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer for user
    
    // Fill opposing party info
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Skip opposing contact (optional)
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Select unknown for opposing lawyer
    await page.getByRole('button', { name: /Unknown/i }).click();
    
    // Should skip opposing lawyer details and go to court info
    await expect(page.locator('#daMainQuestion')).toContainText('Court Information');
  });
});

// ============================================================================
// TEST SUITE 6: CHILDREN INFORMATION FLOW
// ============================================================================

test.describe('Children Information Paths', () => {
  async function navigateToChildren(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip orders
    
    // Fill minimal required info
    await fillUserInfo(page);
    await fillContactInfo(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    // Fill opposing party
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
    
    // Court info - no file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
  }

  test('Has children - collects child details', async ({ page }) => {
    await navigateToChildren(page);
    
    // Say yes to children
    await page.getByRole('button', { name: /^Yes$/i }).click();
    
    // Should ask how many
    await expect(page.locator('#daMainQuestion')).toContainText('Children Information');
    
    // Enter 2 children
    await page.fill('input[type="number"]', '2');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should ask for first child
    await expect(page.locator('#daMainQuestion')).toContainText('Information for Child 1');
    
    // Fill first child
    await page.fill('input[name*="name.first"]', 'Billy');
    await page.fill('input[name*="name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/2015');
    await page.selectOption('select[name*="lives_with"]', 'Both (shared)');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should ask for second child
    await expect(page.locator('#daMainQuestion')).toContainText('Information for Child 2');
    
    // Fill second child
    await page.fill('input[name*="name.first"]', 'Sally');
    await page.fill('input[name*="name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/2017');
    await page.selectOption('select[name*="lives_with"]', 'Me');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should reach summary
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Billy Smith');
    await expect(page.locator('body')).toContainText('Sally Smith');
    await expect(page.locator('body')).toContainText('Number of Children: 2');
  });

  test('No children - skips to summary', async ({ page }) => {
    await navigateToChildren(page);
    
    // Say no to children
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Should go directly to summary
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Children: None');
  });
});

// ============================================================================
// TEST SUITE 7: COURT INFORMATION VARIATIONS
// ============================================================================

test.describe('Court Information Paths', () => {
  async function navigateToCourt(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip orders
    
    // Fill minimal required info
    await fillUserInfo(page);
    await fillContactInfo(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    // Fill opposing party
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
  }

  test('Existing court file - collects details', async ({ page }) => {
    await navigateToCourt(page);
    
    // Select existing file
    await page.locator('input[value="True"]').first().check();
    
    // Court fields should appear
    await expect(page.locator('select[name*="court.name"]')).toBeVisible();
    
    // Fill court details
    await page.selectOption('select[name*="court.name"]', 'Superior Court of Justice');
    await page.fill('input[name*="court.location"]', 'Toronto');
    await page.fill('input[name*="court.file_number"]', 'CV-2024-123456');
    
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to children
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have children');
  });

  test('No existing court file - skips details', async ({ page }) => {
    await navigateToCourt(page);
    
    // Select no existing file
    await page.locator('input[value="False"]').first().check();
    
    // Court fields should NOT appear
    await expect(page.locator('select[name*="court.name"]')).not.toBeVisible();
    
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to children
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have children');
  });
});

// ============================================================================
// TEST SUITE 8: COMPLETE FLOW INTEGRATION TESTS
// ============================================================================

test.describe('Complete Flow Integration', () => {
  test('Full emergency flow with all options', async ({ page }) => {
    await startInterview(page);
    
    // Emergency path
    await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
    await page.getByRole('button', { name: /Continue.*understand/i }).click();
    await page.getByRole('button', { name: /Emergency - will complete after/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Married with divorce and financial orders
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByLabel(/Divorce/).check();
    await page.getByLabel(/Child support/).check();
    await page.getByLabel(/Restraining order/).check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Financial info
    await page.locator('input[value="True"]').first().check(); // Claiming support
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // User info
    await fillUserInfo(page, { alsoKnownAs: 'Johnny Smith' });
    await fillContactInfo(page, { email: 'john@example.com', unit: '10' });
    
    // Has lawyer
    await page.getByRole('button', { name: /^Yes$/i }).click();
    await page.fill('input[name*="name.text"]', 'Legal Representative');
    await page.fill('input[name*="lsuc_number"]', 'L99999');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.fill('input[name*="address.address"]', '200 Legal St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5J 1A1');
    await page.fill('input[name*="phone_number"]', '416-555-9999');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Other party
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    await page.getByRole('button', { name: /^Yes$/i }).click(); // Has lawyer
    await page.fill('input[name*="name.text"]', 'Other Lawyer');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    
    // Court info
    await page.locator('input[value="True"]').first().check();
    await page.selectOption('select[name*="court.name"]', 'Superior Court of Justice');
    await page.fill('input[name*="court.location"]', 'Toronto');
    await page.fill('input[name*="court.file_number"]', 'FL-2024-999');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Children
    await page.getByRole('button', { name: /^Yes$/i }).click();
    await page.fill('input[type="number"]', '1');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.fill('input[name*="name.first"]', 'Bobby');
    await page.fill('input[name*="name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/2020');
    await page.selectOption('select[name*="lives_with"]', 'Both (shared)');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should reach summary with all info
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('Divorce');
    await expect(page.locator('body')).toContainText('Child support');
    await expect(page.locator('body')).toContainText('Restraining order');
    await expect(page.locator('body')).toContainText('John Smith');
    await expect(page.locator('body')).toContainText('Legal Representative');
    await expect(page.locator('body')).toContainText('Jane Doe');
    await expect(page.locator('body')).toContainText('Bobby Smith');
    await expect(page.locator('body')).toContainText('Form 8 - Application');
    await expect(page.locator('body')).toContainText('Form 14B - Motion');
  });

  test('Minimal flow - never together, no lawyers, no children', async ({ page }) => {
    await startInterview(page);
    
    // No emergency
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // MIP completed
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    
    // Never together
    await page.getByRole('button', { name: /Never lived together/i }).click();
    
    // No orders selected
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // User info - minimal
    await fillUserInfo(page);
    await fillContactInfo(page);
    
    // No lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Other party - minimal
    await page.fill('input[name*="opposing_party.name.first"]', 'Ex');
    await page.fill('input[name*="opposing_party.name.last"]', 'Partner');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    
    // No opposing lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // No court file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No children
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Should reach summary
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Never Together');
    await expect(page.locator('body')).toContainText('Self-represented');
    await expect(page.locator('body')).toContainText('Children: None');
    await expect(page.locator('body')).toContainText('Court File: No existing file');
  });
});

// ============================================================================
// TEST SUITE 9: FORM RECOMMENDATIONS LOGIC
// ============================================================================

test.describe('Form Recommendations', () => {
  test('Emergency forms recommended correctly', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
    await page.getByRole('button', { name: /Continue.*understand/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByLabel(/Restraining order/).check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Quick fill to reach summary
    await fillUserInfo(page);
    await fillContactInfo(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
    await page.locator('input[value="False"]').first().check(); // No court file
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No children
    
    // Check emergency forms are recommended
    await expect(page.locator('body')).toContainText('URGENT - File These Today');
    await expect(page.locator('body')).toContainText('Form 8 - Application');
    await expect(page.locator('body')).toContainText('Form 14B - Motion');
    await expect(page.locator('body')).toContainText('Form 25F - Restraining Order');
  });

  test('Divorce forms recommended correctly', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByLabel(/Divorce/).check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Quick fill to reach summary
    await fillUserInfo(page);
    await fillContactInfo(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
    await page.locator('input[value="False"]').first().check(); // No court file
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No children
    
    // Check divorce form is recommended
    await expect(page.locator('body')).toContainText('Form 8A - Application (Divorce)');
  });

  test('Financial forms recommended when needed', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByLabel(/Child support/).check();
    await page.getByLabel(/Property division/).check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Fill financial info
    await page.locator('input[value="True"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Quick fill to reach summary
    await fillUserInfo(page);
    await fillContactInfo(page);
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
    await page.locator('input[value="False"]').first().check(); // No court file
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /^No$/i }).click(); // No children
    
    // Check financial forms are recommended
    await expect(page.locator('body')).toContainText('Form 13 - Financial Statement (Support)');
    await expect(page.locator('body')).toContainText('Form 13.1 - Financial Statement (Property)');
  });
});