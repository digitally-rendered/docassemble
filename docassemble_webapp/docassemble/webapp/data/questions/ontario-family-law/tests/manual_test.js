// Manual test to verify the enhanced common intake form validations
// Run this in browser console while on the interview page

console.log("Testing Enhanced Common Intake Validations");
console.log("==========================================");

// Test 1: Check if phone fields have phone datatype
const phoneFields = document.querySelectorAll('input[name*="phone"]');
console.log(`Found ${phoneFields.length} phone fields`);
phoneFields.forEach(field => {
    console.log(`- ${field.name}: type=${field.type}, pattern=${field.pattern}`);
});

// Test 2: Check if date fields have max/min attributes  
const dateFields = document.querySelectorAll('input[type="date"]');
console.log(`\nFound ${dateFields.length} date fields`);
dateFields.forEach(field => {
    console.log(`- ${field.name}: max=${field.max}, min=${field.min}`);
});

// Test 3: Check if postal code fields have validation
const postalFields = document.querySelectorAll('input[name*="postal"]');
console.log(`\nFound ${postalFields.length} postal code fields`);
postalFields.forEach(field => {
    console.log(`- ${field.name}: pattern=${field.pattern}, placeholder=${field.placeholder}`);
});

// Test 4: Check if contact preference is using radio buttons
const contactPrefRadios = document.querySelectorAll('input[name="user.contact_preference"][type="radio"]');
console.log(`\nFound ${contactPrefRadios.length} contact preference radio buttons`);
contactPrefRadios.forEach(radio => {
    console.log(`- Value: ${radio.value}, Checked: ${radio.checked}`);
});

// Test 5: Check if address field has autocomplete
const addressFields = document.querySelectorAll('input[name*="address.address"]');
console.log(`\nFound ${addressFields.length} address fields`);
addressFields.forEach(field => {
    console.log(`- ${field.name}: autocomplete=${field.autocomplete}`);
});

// Test validation by filling invalid data
console.log("\n=== Testing Validations ===");

// Function to test field validation
function testFieldValidation(fieldName, invalidValue, validValue) {
    const field = document.querySelector(`input[name="${fieldName}"]`);
    if (field) {
        // Try invalid value
        field.value = invalidValue;
        field.dispatchEvent(new Event('change', { bubbles: true }));
        field.dispatchEvent(new Event('blur', { bubbles: true }));
        
        // Check for error
        const errorElement = field.closest('.form-group')?.querySelector('.da-field-error, .text-danger, .help-block');
        const hasError = errorElement && errorElement.textContent.length > 0;
        
        console.log(`${fieldName}:`);
        console.log(`  Invalid value "${invalidValue}": ${hasError ? 'Error shown ✓' : 'No error ✗'}`);
        
        // Try valid value
        field.value = validValue;
        field.dispatchEvent(new Event('change', { bubbles: true }));
        
        const stillHasError = errorElement && errorElement.textContent.length > 0;
        console.log(`  Valid value "${validValue}": ${!stillHasError ? 'Error cleared ✓' : 'Error persists ✗'}`);
    } else {
        console.log(`Field ${fieldName} not found on current page`);
    }
}

// Test postal code validation
testFieldValidation('user.address.postal_code', 'ABC123', 'M5V 3A8');

// Test LSO number validation  
testFieldValidation('user_lawyer.lsuc_number', 'ABC123', '12345A');

// Test phone formatting
const phoneField = document.querySelector('input[name="user.phone_number"]');
if (phoneField) {
    phoneField.value = '4165551234';
    phoneField.dispatchEvent(new Event('change', { bubbles: true }));
    console.log(`Phone formatting: Input "4165551234", Display: "${phoneField.value}"`);
}

console.log("\n=== Test Complete ===");
console.log("Check the console output above for validation results");