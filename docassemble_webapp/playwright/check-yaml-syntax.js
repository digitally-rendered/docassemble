const fs = require('fs');
const yaml = require('js-yaml');

const filePath = '/Users/draw/development/docassemble/docassemble_webapp/docassemble/webapp/data/questions/ontario-family-law/ontario-family-law-wizard.yml';

console.log('CHECKING YAML SYNTAX');
console.log('====================\n');

try {
  const fileContents = fs.readFileSync(filePath, 'utf8');
  
  // Split by --- to handle multiple documents
  const documents = fileContents.split(/^---$/m);
  
  let docCount = 0;
  for (const doc of documents) {
    if (doc.trim()) {
      docCount++;
      try {
        yaml.load(doc);
        console.log(`Document ${docCount}: ✅ Valid YAML`);
      } catch (e) {
        console.log(`Document ${docCount}: ❌ Invalid YAML`);
        console.log('Error:', e.message);
        
        // Try to extract line number
        if (e.mark) {
          console.log(`Line: ${e.mark.line + 1}, Column: ${e.mark.column + 1}`);
        }
      }
    }
  }
  
  console.log(`\nTotal documents: ${docCount}`);
  
} catch (error) {
  console.error('File error:', error.message);
}

console.log('\n====================');
console.log('YAML check complete');