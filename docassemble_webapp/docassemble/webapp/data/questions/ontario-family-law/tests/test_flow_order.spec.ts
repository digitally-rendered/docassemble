import { test, expect } from '@playwright/test';

test('Test complete flow order with MIP after relationship for married', async ({ page }) => {
  console.log('Testing flow order...\n');
  
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_final.yml');
  await page.waitForLoadState('networkidle');
  
  let pageNum = 1;
  
  // 1. Introduction
  let pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // 2. Emergency
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  
  // 3. Relationship status (should be BEFORE MIP)
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  
  if (pageText?.includes('relationship')) {
    console.log('   ✅ Relationship status comes BEFORE MIP (correct!)');
  } else {
    console.log('   ❌ Expected relationship status but got:', pageText?.substring(0, 50));
  }
  
  // Select married to trigger MIP
  await page.getByRole('button', { name: /Married/i }).first().click();
  
  // 4. MIP (should appear for married)
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  
  if (pageText?.includes('Mandatory Information Program')) {
    console.log('   ✅ MIP appears AFTER selecting married (correct!)');
  } else {
    console.log('   ❌ Expected MIP but got:', pageText?.substring(0, 50));
  }
  
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  
  // 5. Children question (should be next)
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  
  if (pageText?.includes('children')) {
    console.log('   ✅ Children question appears after MIP (correct!)');
  } else {
    console.log('   ❌ Expected children question but got:', pageText?.substring(0, 50));
  }
  
  await page.getByRole('button', { name: /^No$/i }).click();
  
  // 6. Orders
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. ${pageText?.substring(0, 40)}...`);
  
  if (pageText?.includes('orders')) {
    console.log('   ✅ Orders page appears after children (correct!)');
  } else {
    console.log('   ❌ Expected orders but got:', pageText?.substring(0, 50));
  }
  
  console.log('\n✅ Flow order test complete!');
});

test('Test flow for non-married (no MIP)', async ({ page }) => {
  console.log('Testing non-married flow (should skip MIP)...\n');
  
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_final.yml');
  await page.waitForLoadState('networkidle');
  
  let pageNum = 1;
  
  // Quick navigation
  await page.getByRole('button', { name: /Continue/i }).click(); // Introduction
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click(); // Emergency
  
  // Should be on relationship status
  let pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. Relationship: ${pageText?.substring(0, 30)}...`);
  
  // Select common-law (not married)
  await page.getByRole('button', { name: /Common-law/i }).click();
  
  // Should go straight to children (skip MIP)
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`${pageNum++}. Next page: ${pageText?.substring(0, 30)}...`);
  
  if (pageText?.includes('children')) {
    console.log('   ✅ Children question appears immediately (MIP skipped for non-married!)');
  } else if (pageText?.includes('MIP') || pageText?.includes('Mandatory')) {
    console.log('   ❌ MIP should NOT appear for non-married relationships!');
  } else {
    console.log('   ❓ Unexpected page:', pageText?.substring(0, 50));
  }
  
  console.log('\n✅ Non-married flow test complete!');
});