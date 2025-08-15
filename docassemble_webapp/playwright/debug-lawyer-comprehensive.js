const { chromium } = require('playwright');

/**
 * Comprehensive Debugging Test for Lawyer Form Issue
 * 
 * This test aims to identify why the "Other Party's Lawyer Information" 
 * form doesn't appear when clicking "Yes, they have a lawyer"
 * 
 * Root Cause Analysis Strategy:
 * 1. Video record entire flow for visual analysis
 * 2. Inspect DOM state at each critical step
 * 3. Handle base64 encoded field names properly
 * 4. Add detailed logging at each decision point
 * 5. Test the exact "never lived together" + custody flow
 */

(async () => {
  console.log('🔍 COMPREHENSIVE LAWYER FORM DEBUG');
  console.log('===================================\n');
  
  const browser = await chromium.launch({ 
    headless: false, // Keep visible for debugging
    slowMo: 500 // Add delay between actions for observation
  });
  
  const context = await browser.newContext({
    recordVideo: {
      dir: './test-results/',
      size: { width: 1280, height: 720 }
    }
  });
  
  const page = await context.newPage();
  
  // Enhanced error handling
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🚨 Browser console error:', msg.text());
    }
  });
  
  page.on('pageerror', error => {
    console.log('🚨 Page error:', error.message);
  });
  
  try {
    console.log('📹 Video recording started');
    console.log('🌐 Navigating to wizard...');
    
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // === STEP 1: Navigate through initial screens ===
    console.log('\n📍 STEP 1: Initial Navigation');
    
    // Welcome screen
    await page.screenshot({ path: './debug-step1-welcome.png' });
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Emergency check
    await page.screenshot({ path: './debug-step2-emergency.png' });
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // MIP requirement
    await page.screenshot({ path: './debug-step3-mip.png' });
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    
    // MIP continue
    await page.screenshot({ path: './debug-step4-mip-continue.png' });
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // === STEP 2: Relationship status (CRITICAL: Never lived together) ===
    console.log('📍 STEP 2: Selecting "Never lived together"');
    await page.screenshot({ path: './debug-step5-relationship.png' });
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(1000);
    
    // === STEP 3: Select child custody ===
    console.log('📍 STEP 3: Selecting child custody');
    await page.screenshot({ path: './debug-step6-orders.png' });
    await page.check('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // === STEP 4: Role selection ===
    console.log('📍 STEP 4: Role selection - Applicant');
    await page.screenshot({ path: './debug-step7-role.png' });
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(2000);
    
    // === STEP 5: User Information (Critical - needs proper field handling) ===
    console.log('📍 STEP 5: User Information Form');
    await page.screenshot({ path: './debug-step8-user-info.png' });
    
    // Get all input fields and their names
    const userInputs = await page.locator('input').all();
    console.log(`   Found ${userInputs.length} input fields`);
    
    // Fill user information systematically
    for (let i = 0; i < userInputs.length; i++) {
      const input = userInputs[i];
      const name = await input.getAttribute('name') || '';
      const type = await input.getAttribute('type') || 'text';
      const required = await input.getAttribute('required') !== null;
      
      console.log(`   Field ${i}: name="${name}", type="${type}", required=${required}`);
      
      // Handle base64 encoded field names specifically
      if (required || name.includes('name') || name.includes('date') || name.includes('phone')) {
        try {
          if (type === 'text' && (name.includes('first') || i === 0)) {
            await input.fill('TestFirst');
            console.log(`     ✓ Filled first name`);
          } else if (type === 'text' && (name.includes('last') || i === 2)) {
            await input.fill('TestLast');
            console.log(`     ✓ Filled last name`);
          } else if (type === 'date') {
            await input.fill('1990-01-01');
            console.log(`     ✓ Filled date`);
          } else if (type === 'tel') {
            await input.fill('4165550100');
            console.log(`     ✓ Filled phone`);
          } else if (type === 'text' && required) {
            await input.fill('TestValue');
            console.log(`     ✓ Filled required text field`);
          }
        } catch (e) {
          console.log(`     ⚠️ Failed to fill field ${i}: ${e.message}`);
        }
      }
    }
    
    await page.screenshot({ path: './debug-step9-user-filled.png' });
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // === STEP 6: Other Party Information ===
    console.log('📍 STEP 6: Other Party Information');
    let currentUrl = page.url();
    let content = await page.content();
    console.log(`   Current URL: ${currentUrl}`);
    
    if (content.includes('Other Party')) {
      console.log('   ✓ Other Party form appeared');
      await page.screenshot({ path: './debug-step10-other-party.png' });
      
      // Fill other party info minimally
      const otherInputs = await page.locator('input[type="text"]').all();
      if (otherInputs.length >= 2) {
        await otherInputs[0].fill('OtherFirst');
        await otherInputs[1].fill('OtherLast');
        console.log('   ✓ Filled other party name fields');
      }
      
      await page.screenshot({ path: './debug-step11-other-filled.png' });
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(2000);
    } else {
      console.log('   ⚠️ Other Party form not found - checking current screen');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log(`   Current screen: "${heading}"`);
    }
    
    // === STEP 7: User Lawyer Question ===
    console.log('📍 STEP 7: User Lawyer Question');
    content = await page.content();
    await page.screenshot({ path: './debug-step12-user-lawyer.png' });
    
    if (content.includes('Do you have a lawyer?')) {
      console.log('   ✓ User lawyer question found');
      await page.click('button:has-text("No, I am self-represented")');
      await page.waitForTimeout(2000);
      console.log('   ✓ Selected "No, I am self-represented"');
    } else {
      console.log('   ⚠️ User lawyer question not found');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log(`   Current screen: "${heading}"`);
    }
    
    // === STEP 8: Other Party Lawyer Question (CRITICAL POINT) ===
    console.log('📍 STEP 8: Other Party Lawyer Question (CRITICAL)');
    content = await page.content();
    await page.screenshot({ path: './debug-step13-other-lawyer-question.png' });
    
    if (content.includes('Does the other party have a lawyer?')) {
      console.log('   🎯 OTHER PARTY LAWYER QUESTION FOUND!');
      
      // Get all available buttons
      const allButtons = await page.locator('button').allTextContents();
      console.log('   Available buttons:', allButtons);
      
      // Take screenshot before clicking
      await page.screenshot({ path: './debug-step14-before-yes-click.png' });
      
      console.log('   🔄 Clicking "Yes, they have a lawyer"...');
      await page.click('button:has-text("Yes, they have a lawyer")');
      
      // Wait and observe the transition
      await page.waitForTimeout(3000);
      
      // === STEP 9: Check what happens after clicking Yes ===
      console.log('📍 STEP 9: After Clicking "Yes, they have a lawyer"');
      content = await page.content();
      const heading = await page.locator('h1, h2').first().textContent();
      currentUrl = page.url();
      
      await page.screenshot({ path: './debug-step15-after-yes-click.png' });
      
      console.log(`   Current URL: ${currentUrl}`);
      console.log(`   Current heading: "${heading}"`);
      
      // Check for specific outcomes
      if (content.includes('Lawyer') && content.includes('Information') && content.includes('Other Party')) {
        console.log('   🎉 SUCCESS! Other Party Lawyer form is displayed!');
        
        // Try to interact with the lawyer form
        const lawyerFields = await page.locator('input').count();
        console.log(`   Found ${lawyerFields} fields in lawyer form`);
        
        // Check if the continue button field is present
        const continueField = await page.locator('[name*="collect_other_party_lawyer_info"]').count();
        console.log(`   Continue button field present: ${continueField > 0}`);
        
      } else if (content.includes('Court')) {
        console.log('   ❌ ISSUE CONFIRMED: Skipped to Court Information');
        console.log('   🔍 This confirms the bug - lawyer form was bypassed');
        
        // Check for any JavaScript errors that might have occurred
        const errors = await page.evaluate(() => {
          return window.console ? window.console._logs : [];
        });
        
        if (errors && errors.length > 0) {
          console.log('   JavaScript errors detected:', errors);
        }
        
      } else if (content.includes('Error')) {
        console.log('   ❌ Error page displayed');
        const errorText = await page.locator('body').textContent();
        console.log('   Error details:', errorText.substring(0, 500));
        
      } else {
        console.log('   ❓ Unexpected screen after clicking Yes');
        console.log('   Content preview:', content.substring(0, 500));
      }
      
    } else {
      console.log('   ❌ OTHER PARTY LAWYER QUESTION NOT FOUND');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log(`   Current screen: "${heading}"`);
      console.log('   🔍 This suggests the flow is already broken before this point');
    }
    
    // === FINAL ANALYSIS ===
    console.log('\n📊 FINAL ANALYSIS');
    console.log('==================');
    
    const finalContent = await page.content();
    if (finalContent.includes('show if: other_party_has_lawyer is True')) {
      console.log('✓ YAML condition found in page source');
    } else {
      console.log('⚠️ YAML condition not found - may indicate compilation issue');
    }
    
    // Take final screenshot
    await page.screenshot({ path: './debug-final-state.png' });
    
    console.log('📹 Video recording will be saved to test-results/');
    console.log('🖼️ Screenshots saved with debug-step* naming');
    
  } catch (error) {
    console.error('🚨 Test failed with error:', error);
    await page.screenshot({ path: './debug-error-state.png' });
  } finally {
    console.log('\n🏁 Debug complete. Keeping browser open for manual inspection...');
    console.log('Press Ctrl+C to close when done examining');
    
    // Keep browser open for manual inspection
    await new Promise((resolve) => {
      process.on('SIGINT', () => {
        console.log('\n👋 Closing browser...');
        resolve();
      });
    });
  }
  
  await context.close();
  await browser.close();
})();