#!/usr/bin/env python3
"""
Docassemble Utility: Comprehensive Word document analysis tool
Provides detailed analysis of Word document structure for docassemble integration.
Alternative to non-functional docassemble Admin form field detection.
"""
from docx import Document
import sys

def analyze_word_document(file_path):
    """Analyze a Word document and identify form fields, content controls, and fillable elements"""
    try:
        doc = Document(file_path)
        
        print(f"Analyzing document: {file_path}")
        print("=" * 50)
        
        # Basic document info
        print(f"Number of paragraphs: {len(doc.paragraphs)}")
        print(f"Number of tables: {len(doc.tables)}")
        
        # Look for form fields in paragraphs
        print("\n--- PARAGRAPH ANALYSIS ---")
        form_fields = []
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:
                # Look for common field patterns
                if any(pattern in text.lower() for pattern in ['___', '______', 'name:', 'date:', 'address:', 'phone:', 'email:']):
                    form_fields.append(f"Para {i}: {text}")
                    print(f"Para {i}: {text}")
        
        # Analyze tables for form fields
        print(f"\n--- TABLE ANALYSIS ---")
        table_fields = []
        for table_idx, table in enumerate(doc.tables):
            print(f"\nTable {table_idx + 1}:")
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    if cell_text and any(pattern in cell_text.lower() for pattern in ['___', '______', 'name', 'date', 'address', 'phone', 'email', 'fill', 'enter']):
                        field_info = f"Table {table_idx + 1}, Row {row_idx + 1}, Cell {cell_idx + 1}: {cell_text}"
                        table_fields.append(field_info)
                        print(f"  {field_info}")
        
        # Look for content controls (form fields)
        print(f"\n--- CONTENT CONTROLS ---")
        # Note: python-docx has limited support for content controls
        # We'll look for XML elements that might indicate form fields
        
        # Summary
        print(f"\n--- SUMMARY ---")
        print(f"Potential form fields found in paragraphs: {len(form_fields)}")
        print(f"Potential form fields found in tables: {len(table_fields)}")
        
        return {
            'paragraph_fields': form_fields,
            'table_fields': table_fields,
            'total_paragraphs': len(doc.paragraphs),
            'total_tables': len(doc.tables)
        }
        
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    # Allow file path as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "/Users/draw/Downloads/flr-8-jun25-en.docx"
    
    result = analyze_word_document(file_path)