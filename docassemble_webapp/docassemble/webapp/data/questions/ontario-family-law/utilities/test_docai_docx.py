#!/usr/bin/env python3
"""
Test Document AI with native DOCX support
"""

import os
from pathlib import Path
from google.cloud import documentai_v1 as documentai
import json

# Set environment
os.environ['GCP_PROJECT_ID'] = 'default-456005'
os.environ['GCP_LOCATION'] = 'us'
os.environ['DOCAI_FORM_PARSER_ID'] = '688d4082bdc65cd2'
os.environ['DOCAI_OCR_PROCESSOR_ID'] = '2a844227b1c7aaea'

def process_docx_with_document_ai(file_path: str, processor_type: str = 'form'):
    """
    Process DOCX file with Document AI
    Note: Document AI supports DOCX files directly
    """
    
    client = documentai.DocumentProcessorServiceClient()
    
    # Configure processor
    project_id = os.environ.get('GCP_PROJECT_ID')
    location = os.environ.get('GCP_LOCATION')
    
    if processor_type == 'form':
        processor_id = os.environ.get('DOCAI_FORM_PARSER_ID')
    else:
        processor_id = os.environ.get('DOCAI_OCR_PROCESSOR_ID')
    
    processor_name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    
    print(f"Using processor: {processor_name}")
    print(f"Processing file: {Path(file_path).name}")
    
    # Read file
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Determine MIME type
    if file_path.endswith('.docx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_path.endswith('.doc'):
        mime_type = 'application/msword'
    elif file_path.endswith('.pdf'):
        mime_type = 'application/pdf'
    else:
        mime_type = 'application/octet-stream'
    
    # Create document
    raw_document = documentai.RawDocument(
        content=content,
        mime_type=mime_type
    )
    
    # Configure request with OCR options for better DOCX handling
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document,
        # Enable OCR for embedded images in DOCX
        process_options=documentai.ProcessOptions(
            ocr_config=documentai.OcrConfig(
                enable_native_pdf_parsing=False,  # Force OCR for better extraction
                enable_image_quality_scores=True,
                enable_symbol=True,
                compute_style_info=True,
                disable_character_boxes_detection=False
            )
        )
    )
    
    try:
        # Process document
        print("Processing document...")
        result = client.process_document(request=request)
        
        print(f"Document processed successfully!")
        print(f"Text extracted: {len(result.document.text)} characters")
        
        # Extract structured data
        fields = []
        
        # Extract form fields
        if hasattr(result.document, 'pages'):
            for page_idx, page in enumerate(result.document.pages):
                print(f"\nPage {page_idx + 1}:")
                
                # Form fields
                if hasattr(page, 'form_fields'):
                    print(f"  Form fields found: {len(page.form_fields)}")
                    for field_idx, form_field in enumerate(page.form_fields):
                        field_name = get_text(form_field.field_name, result.document)
                        field_value = get_text(form_field.field_value, result.document)
                        
                        if field_name or field_value:
                            fields.append({
                                'type': 'form_field',
                                'name': field_name,
                                'value': field_value,
                                'confidence': form_field.field_name.confidence if form_field.field_name else 0,
                                'page': page_idx + 1
                            })
                            
                            print(f"    Field: {field_name[:50]} = {field_value[:50] if field_value else 'blank'}")
                
                # Tables
                if hasattr(page, 'tables'):
                    print(f"  Tables found: {len(page.tables)}")
                    for table_idx, table in enumerate(page.tables):
                        print(f"    Table {table_idx + 1}: {len(table.header_rows)} headers, {len(table.body_rows)} rows")
                
                # Paragraphs
                if hasattr(page, 'paragraphs'):
                    print(f"  Paragraphs found: {len(page.paragraphs)}")
                
                # Lines
                if hasattr(page, 'lines'):
                    print(f"  Lines found: {len(page.lines)}")
        
        # Extract entities
        if hasattr(result.document, 'entities'):
            print(f"\nEntities found: {len(result.document.entities)}")
            for entity in result.document.entities[:10]:  # First 10
                fields.append({
                    'type': 'entity',
                    'name': entity.type_,
                    'value': entity.mention_text[:100],
                    'confidence': entity.confidence
                })
                print(f"  {entity.type_}: {entity.mention_text[:50]}")
        
        # Extract key-value pairs
        if hasattr(result.document, 'document_layout'):
            layout = result.document.document_layout
            if hasattr(layout, 'blocks'):
                print(f"\nLayout blocks found: {len(layout.blocks)}")
        
        return fields, result.document
        
    except Exception as e:
        print(f"Error processing document: {e}")
        
        # Check if it's a MIME type issue
        if "UNSUPPORTED_MIME_TYPE" in str(e):
            print("\nNote: This processor may not support DOCX directly.")
            print("Solutions:")
            print("1. Use the OCR processor instead of Form Parser")
            print("2. Convert DOCX to PDF first")
            print("3. Use Enterprise Document OCR processor (if available)")
        
        return [], None

def get_text(layout, document):
    """Extract text from Document AI layout element"""
    if not layout or not hasattr(layout, 'text_anchor'):
        return ""
    
    text = ""
    if layout.text_anchor and layout.text_anchor.text_segments:
        for segment in layout.text_anchor.text_segments:
            start = segment.start_index if hasattr(segment, 'start_index') else 0
            end = segment.end_index if hasattr(segment, 'end_index') else len(document.text)
            text += document.text[start:end]
    
    return text.strip()

def test_both_processors(file_path: str):
    """Test both Form Parser and OCR processors"""
    
    print("=" * 80)
    print("DOCUMENT AI DOCX PROCESSING TEST")
    print("=" * 80)
    
    # Test with Form Parser
    print("\n1. Testing with FORM PARSER:")
    print("-" * 40)
    form_fields, form_doc = process_docx_with_document_ai(file_path, 'form')
    
    # Test with OCR Processor
    print("\n2. Testing with OCR PROCESSOR:")
    print("-" * 40)
    ocr_fields, ocr_doc = process_docx_with_document_ai(file_path, 'ocr')
    
    # Compare results
    print("\n" + "=" * 80)
    print("COMPARISON:")
    print(f"Form Parser extracted: {len(form_fields)} fields")
    print(f"OCR Processor extracted: {len(ocr_fields)} fields")
    
    # Save results
    results = {
        'file': file_path,
        'form_parser': {
            'fields': form_fields,
            'text_length': len(form_doc.text) if form_doc else 0
        },
        'ocr_processor': {
            'fields': ocr_fields,
            'text_length': len(ocr_doc.text) if ocr_doc else 0
        }
    }
    
    output_file = f"docai_test_{Path(file_path).stem}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Default test file
        test_file = "workflow_output/ontario_forms/financial_statements/form_13_-_financial_statement_support_flr-13-may21-en-fil.docx"
        
        if not os.path.exists(test_file):
            test_file = "workflow_output/ontario_forms/applications/form_8_-_application_general_flr-8-jun25-en-fil.docx"
    
    if os.path.exists(test_file):
        test_both_processors(test_file)
    else:
        print(f"File not found: {test_file}")
        print("Please provide a valid DOCX file path")