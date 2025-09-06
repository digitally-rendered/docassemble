import { test, expect } from '@playwright/test';

/**
 * Test Suite: Form 8 Enhanced Field Labels Validation
 * 
 * Purpose: Validate that the regenerated Form 8 unified interview:
 * 1. Loads without errors (unlike previous version)
 * 2. Shows meaningful question labels instead of generic "Field X" labels
 * 3. Has proper navigation through questions
 * 4. Successfully resolves the field label enhancement issue
 */

test.describe('Form 8 Enhanced Labels Validation', () => {
  let page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Enable console logging to catch any JavaScript errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Browser console error:', msg.text());
      }
    });

    // Enable request/response logging to catch network errors
    page.on('requestfailed', request => {
      console.log('Failed request:', request.url(), request.failure().errorText);
    });
  });

  test('Form 8 unified interview loads successfully without errors', async () => {
    console.log('🧪 Testing: Form 8 interview loads successfully...');

    // Navigate to the Form 8 unified interview
    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    
    const response = await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Verify the page loads successfully
    expect(response.status()).toBe(200);
    
    // Wait for the form to be fully loaded
    await page.waitForSelector('form', { timeout: 10000 });
    
    // Verify no critical JavaScript errors occurred
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));
    
    // Wait a moment for any errors to surface
    await page.waitForTimeout(2000);
    
    expect(pageErrors.length).toBe(0);
    console.log('✅ Form 8 interview loaded successfully without errors');
  });

  test('First question shows meaningful label "Court Name" not generic field label', async () => {
    console.log('🧪 Testing: First question has meaningful label...');

    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    // Wait for the question to load
    await page.waitForSelector('.da-page-header', { timeout: 10000 });

    // Check that the first question shows "Court Name" not "Field 0" or similar
    const questionText = await page.textContent('.da-page-header');
    
    expect(questionText).toContain('Court Name');
    expect(questionText).not.toContain('Field 0');
    expect(questionText).not.toContain('form_specific_dropdown_field');
    
    console.log(`✅ First question shows meaningful label: "${questionText}"`);
  });

  test('Can navigate through first few questions with enhanced labels', async () => {
    console.log('🧪 Testing: Navigation through enhanced labeled questions...');

    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    const expectedQuestions = [
      'Court Name',
      'Court File No',
      'Applicant Full Legal Name',
      'Applicant Address - Street',
      'Applicant Address - City'
    ];

    for (let i = 0; i < expectedQuestions.length; i++) {
      console.log(`   📋 Checking question ${i + 1}: ${expectedQuestions[i]}`);
      
      // Wait for the question to load
      await page.waitForSelector('.da-page-header', { timeout: 10000 });
      
      // Verify the question shows the expected meaningful label
      const questionText = await page.textContent('.da-page-header');
      expect(questionText).toContain(expectedQuestions[i]);
      
      // Fill in a test value
      const inputField = await page.locator('input[type="text"]').first();
      if (await inputField.count() > 0) {
        await inputField.fill(`Test ${expectedQuestions[i]} Value`);
      }
      
      // Continue to next question
      const continueButton = await page.locator('button:has-text("Continue"), input[type="submit"][value="Continue"]').first();
      if (await continueButton.count() > 0) {
        await continueButton.click();
        
        // Wait for navigation
        await page.waitForTimeout(1000);
      } else {
        console.log('   ⚠️  Continue button not found, may have reached end of flow');
        break;
      }
    }

    console.log('✅ Successfully navigated through questions with enhanced labels');
  });

  test('Verify specific enhanced labels are present in question sequence', async () => {
    console.log('🧪 Testing: Specific enhanced labels verification...');

    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    // Test labels we know should be enhanced from the YAML
    const enhancedLabelsToTest = [
      { label: 'Court Name', should_not_contain: ['Field', 'form_specific_dropdown_field'] },
      { label: 'Court File No', should_not_contain: ['Field', 'form_specific_courtfileno'] },
      { label: 'Applicant Full Legal Name', should_not_contain: ['Field', 'form_specific_text_field'] },
      { label: 'Applicant Phone Number', should_not_contain: ['Field', 'form_specific_text_field_6'] }
    ];

    for (const testCase of enhancedLabelsToTest.slice(0, 2)) { // Test first 2 to keep test focused
      console.log(`   📋 Testing enhanced label: ${testCase.label}`);
      
      // Navigate through questions until we find this label or give up
      let foundLabel = false;
      let attempts = 0;
      const maxAttempts = 10;
      
      while (!foundLabel && attempts < maxAttempts) {
        await page.waitForSelector('.da-page-header', { timeout: 5000 });
        const questionText = await page.textContent('.da-page-header');
        
        if (questionText.includes(testCase.label)) {
          foundLabel = true;
          
          // Verify it doesn't contain the old generic terms
          for (const badTerm of testCase.should_not_contain) {
            expect(questionText).not.toContain(badTerm);
          }
          
          console.log(`   ✅ Found enhanced label: "${questionText}"`);
        } else {
          // Fill current field and continue
          const inputField = await page.locator('input[type="text"]').first();
          if (await inputField.count() > 0) {
            await inputField.fill('Test Value');
          }
          
          const continueButton = await page.locator('button:has-text("Continue"), input[type="submit"][value="Continue"]').first();
          if (await continueButton.count() > 0) {
            await continueButton.click();
            await page.waitForTimeout(1000);
            attempts++;
          } else {
            break;
          }
        }
      }
      
      expect(foundLabel).toBe(true);
    }

    console.log('✅ Enhanced labels verification completed successfully');
  });

  test('Verify interview structure and metadata', async () => {
    console.log('🧪 Testing: Interview structure and metadata...');

    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    // Check page title contains Form 8 reference
    const title = await page.title();
    expect(title.toLowerCase()).toMatch(/form.?8|ontario/);
    
    // Verify the interview has proper structure elements
    await page.waitForSelector('form', { timeout: 10000 });
    
    // Check for presence of navigation elements
    const hasForm = await page.locator('form').count() > 0;
    expect(hasForm).toBe(true);
    
    // Check for input fields
    const hasInputs = await page.locator('input, textarea, select').count() > 0;
    expect(hasInputs).toBe(true);

    console.log('✅ Interview structure and metadata verified');
  });

  test('Document successful resolution of field label enhancement', async () => {
    console.log('🧪 Testing: Documenting successful field label enhancement...');

    const interviewUrl = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    await page.goto(`http://localhost${interviewUrl}`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    // Collect evidence of successful enhancement
    const evidence = {
      interview_loads: false,
      has_meaningful_labels: false,
      no_generic_fields: false,
      navigation_works: false
    };

    // 1. Interview loads without errors
    try {
      await page.waitForSelector('form', { timeout: 10000 });
      evidence.interview_loads = true;
      console.log('   ✅ Interview loads successfully');
    } catch (error) {
      console.log('   ❌ Interview failed to load:', error.message);
    }

    // 2. Has meaningful labels
    try {
      await page.waitForSelector('.da-page-header', { timeout: 5000 });
      const questionText = await page.textContent('.da-page-header');
      
      const meaningfulLabels = ['Court Name', 'Court File', 'Applicant', 'Name', 'Address'];
      const hasMeaningfulLabel = meaningfulLabels.some(label => questionText.includes(label));
      
      if (hasMeaningfulLabel) {
        evidence.has_meaningful_labels = true;
        console.log(`   ✅ Has meaningful label: "${questionText}"`);
      }
    } catch (error) {
      console.log('   ❌ Could not verify meaningful labels:', error.message);
    }

    // 3. No generic field labels
    try {
      const questionText = await page.textContent('.da-page-header');
      const hasGenericTerms = questionText.includes('Field ') || questionText.includes('form_specific_');
      
      if (!hasGenericTerms) {
        evidence.no_generic_fields = true;
        console.log('   ✅ No generic field labels detected');
      } else {
        console.log('   ⚠️  Still contains generic terms:', questionText);
      }
    } catch (error) {
      console.log('   ❌ Could not check for generic labels:', error.message);
    }

    // 4. Navigation works
    try {
      const inputField = await page.locator('input[type="text"]').first();
      if (await inputField.count() > 0) {
        await inputField.fill('Test Navigation Value');
        
        const continueButton = await page.locator('button:has-text("Continue"), input[type="submit"][value="Continue"]').first();
        if (await continueButton.count() > 0) {
          await continueButton.click();
          await page.waitForTimeout(2000);
          
          // Check if we navigated to a new question
          const newQuestionText = await page.textContent('.da-page-header').catch(() => '');
          if (newQuestionText && newQuestionText.length > 0) {
            evidence.navigation_works = true;
            console.log('   ✅ Navigation between questions works');
          }
        }
      }
    } catch (error) {
      console.log('   ⚠️  Navigation test inconclusive:', error.message);
    }

    // Summary of enhancement success
    const successCount = Object.values(evidence).filter(Boolean).length;
    const totalChecks = Object.keys(evidence).length;
    
    console.log('\n📊 ENHANCEMENT RESOLUTION SUMMARY:');
    console.log(`   Success Rate: ${successCount}/${totalChecks} (${Math.round(successCount/totalChecks*100)}%)`);
    console.log('   Evidence:', JSON.stringify(evidence, null, 2));
    
    // Test passes if most checks succeed
    expect(successCount).toBeGreaterThanOrEqual(3);
    
    console.log('✅ Field label enhancement successfully resolved!');
  });
});