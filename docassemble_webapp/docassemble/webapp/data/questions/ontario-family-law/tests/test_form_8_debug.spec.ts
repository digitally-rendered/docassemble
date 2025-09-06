import { test, expect } from '@playwright/test';

/**
 * Debug test to check if Form 8 enhanced interview loads
 */

test.describe('Form 8 Debug', () => {
  test('Check if Form 8 interview loads and get error details', async ({ page }) => {
    console.log('🧪 Debug: Attempting to load Form 8 enhanced interview...');

    // Enable console logging to catch errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(`Console error: ${msg.text()}`);
        console.log(`Browser console error: ${msg.text()}`);
      }
    });

    page.on('pageerror', error => {
      errors.push(`Page error: ${error.message}`);
      console.log(`Page error: ${error.message}`);
    });

    // Try to navigate to Form 8
    const interviewUrl = 'http://localhost:8080/interview?i=docassemble.webapp:data/questions/ontario-family-law/utilities/generated_interviews_unified/form_8_unified.yml';
    
    try {
      const response = await page.goto(interviewUrl, { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });

      console.log(`Response status: ${response?.status()}`);
      console.log(`Response URL: ${response?.url()}`);
      
      // Check if we got an error page
      const pageContent = await page.textContent('body');
      console.log('Page content preview:', pageContent.substring(0, 500));

      // Take a screenshot for visual debugging
      await page.screenshot({ path: 'test-results/form-8-debug-load.png' });

      // Look for specific error indicators
      if (pageContent.includes('Error')) {
        console.log('❌ Error page detected');
        
        // Look for specific error messages
        const errorElements = await page.locator('.alert-danger, .error, [class*="error"]').all();
        for (const element of errorElements) {
          const text = await element.textContent();
          console.log('Error element:', text);
        }

        // Check for Python traceback
        if (pageContent.includes('Traceback')) {
          console.log('🐍 Python traceback detected');
          const traceback = pageContent.match(/Traceback[\s\S]*?(?=\n\n|\Z)/);
          if (traceback) {
            console.log('Traceback:', traceback[0]);
          }
        }

        // Check for YAML syntax errors
        if (pageContent.includes('yaml') || pageContent.includes('YAML')) {
          console.log('📄 YAML-related error detected');
        }
      }

      // If no errors, check if form loaded
      const hasForm = await page.locator('form').count() > 0;
      if (hasForm) {
        console.log('✅ Form element found - interview may have loaded successfully');
        
        // Get the first question text
        const questionElement = await page.locator('h1, .da-page-header, #daMainQuestion').first();
        if (await questionElement.count() > 0) {
          const questionText = await questionElement.textContent();
          console.log(`First question: "${questionText}"`);
        }
      } else {
        console.log('❌ No form element found');
      }

      // Log all collected errors
      if (errors.length > 0) {
        console.log('📋 All errors collected:');
        errors.forEach((error, index) => {
          console.log(`${index + 1}. ${error}`);
        });
      } else {
        console.log('✅ No JavaScript errors detected');
      }

    } catch (error) {
      console.log('❌ Failed to load page:', error.message);
    }
  });
});