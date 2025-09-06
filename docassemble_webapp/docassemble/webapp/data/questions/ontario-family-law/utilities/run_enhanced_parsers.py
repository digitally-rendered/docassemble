#!/usr/bin/env python3
"""
Run enhanced parsers on Ontario Family Law forms to detect ALL fields including long-form text areas
"""

import json
from pathlib import Path
from typing import Dict, List
import sys

# Import our enhanced parsers
from long_form_field_detector import LongFormFieldDetector
from precise_field_mapper import PreciseFieldMapper


def run_enhanced_parsing():
    """Run enhanced parsing on all forms, especially those with long-form fields"""
    
    # Priority forms known to have long-form fields
    priority_forms = {
        "8": "Application (General)",
        "8A": "Application (Divorce)", 
        "10": "Answer",
        "36": "Affidavit for Divorce",
        "17A": "Case Conference Brief",
        "17C": "Settlement Conference Brief",
        "13A": "Certificate of Financial Disclosure",
        "29A": "Notice of Garnishment (Lump Sum)",
        "29B": "Notice of Garnishment (Periodic)",
        "33F": "Access Application",
        "36A": "Certificate of Divorce"
    }
    
    # Paths to check for forms
    form_paths = [
        Path("workflow_output/ontario_forms"),
        Path("workflow_output/downloads"),
        Path("ontario_forms_test"),
        Path("test_download")
    ]
    
    # Find the directory with forms
    forms_dir = None
    for path in form_paths:
        if path.exists():
            forms_dir = path
            print(f"📁 Found forms in: {forms_dir}")
            break
    
    if not forms_dir:
        print("❌ No forms directory found")
        return
    
    # Process each priority form
    results = {}
    
    for form_num, form_title in priority_forms.items():
        print(f"\n{'='*60}")
        print(f"🔍 Processing Form {form_num}: {form_title}")
        print(f"{'='*60}")
        
        # Find the form file
        form_file = None
        
        # Try different patterns
        patterns = [
            f"**/form_{form_num}_*.docx",
            f"**/form_{form_num}_*.pdf",
            f"**/form_{form_num.lower()}_*.docx",
            f"**/form_{form_num.lower()}_*.pdf",
            f"**/*flr-{form_num}*.docx",
            f"**/*flr-{form_num}*.pdf",
            f"**/*flr-{form_num.lower()}*.docx",
            f"**/*flr-{form_num.lower()}*.pdf"
        ]
        
        for pattern in patterns:
            matches = list(forms_dir.rglob(pattern))
            if matches:
                # Prefer DOCX over PDF for better field mapping
                docx_files = [f for f in matches if f.suffix.lower() == '.docx']
                if docx_files:
                    form_file = docx_files[0]
                else:
                    form_file = matches[0]
                break
        
        if not form_file:
            print(f"⚠️  Form {form_num} file not found")
            results[form_num] = {"status": "not_found"}
            continue
        
        print(f"📄 Found file: {form_file}")
        
        # Run different parsers based on file type
        form_results = {
            "file": str(form_file),
            "fields": {}
        }
        
        if form_file.suffix.lower() == '.docx':
            # Use precise field mapper for DOCX
            print("\n🎯 Running Precise Field Mapper...")
            try:
                mapper = PreciseFieldMapper(str(form_file))
                fields = mapper.map_all_fields()
                
                # Categorize fields
                field_summary = {
                    "total": len(fields),
                    "by_type": {},
                    "by_location": {},
                    "long_form_fields": []
                }
                
                for field in fields:
                    # Count by type
                    field_type = field.field_type
                    field_summary["by_type"][field_type] = field_summary["by_type"].get(field_type, 0) + 1
                    
                    # Count by location
                    location = field.location_type
                    field_summary["by_location"][location] = field_summary["by_location"].get(location, 0) + 1
                    
                    # Identify long-form fields
                    if field.field_type == "area" or "detail" in field.field_label.lower() or "explain" in field.field_label.lower():
                        field_summary["long_form_fields"].append({
                            "id": field.field_id,
                            "label": field.field_label,
                            "location": field.get_unique_signature()
                        })
                
                form_results["fields"]["precise_mapper"] = field_summary
                
                # Export detailed map
                export_file = Path(f"parsed_forms/form_{form_num}_precise_map.json")
                export_data = mapper.export_field_map(str(export_file))
                print(f"  ✅ Exported {len(fields)} fields to {export_file}")
                
                # Show summary
                print(f"  📊 Field Summary:")
                print(f"     Total: {field_summary['total']}")
                print(f"     By Type: {field_summary['by_type']}")
                print(f"     By Location: {field_summary['by_location']}")
                print(f"     Long-form: {len(field_summary['long_form_fields'])}")
                
                if field_summary["long_form_fields"]:
                    print(f"  📝 Long-form fields detected:")
                    for lf in field_summary["long_form_fields"][:3]:  # Show first 3
                        print(f"     - {lf['label'][:60]}...")
                
            except Exception as e:
                print(f"  ❌ Error in precise mapper: {e}")
                form_results["fields"]["precise_mapper"] = {"error": str(e)}
        
        # Also run long-form detector
        if form_file.suffix.lower() in ['.pdf', '.docx']:
            print("\n📜 Running Long-Form Field Detector...")
            try:
                detector = LongFormFieldDetector()
                long_fields = detector.detect_long_form_fields(str(form_file), form_num)
                
                if long_fields:
                    print(f"  ✅ Found {len(long_fields)} long-form fields:")
                    for field in long_fields[:5]:  # Show first 5
                        print(f"     - {field.label[:60]}...")
                        if field.prompt != field.label:
                            print(f"       Prompt: {field.prompt[:60]}...")
                
                # Convert to standard format
                enhanced_fields = []
                for lf_field in long_fields:
                    enhanced_fields.append({
                        "field_id": lf_field.field_id,
                        "field_name": f"form{form_num}_{lf_field.field_id}",
                        "field_type": "area",
                        "field_label": lf_field.label,
                        "prompt": lf_field.prompt,
                        "section": lf_field.section,
                        "required": lf_field.required,
                        "estimated_lines": lf_field.estimated_lines,
                        "page_number": lf_field.page_number
                    })
                
                form_results["fields"]["long_form_detector"] = {
                    "total": len(enhanced_fields),
                    "fields": enhanced_fields
                }
                
            except Exception as e:
                print(f"  ❌ Error in long-form detector: {e}")
                form_results["fields"]["long_form_detector"] = {"error": str(e)}
        
        # Update existing parsed data with new fields
        existing_file = Path(f"parsed_forms/form_{form_num}_fields.json")
        if existing_file.exists():
            print("\n🔄 Updating existing parsed data...")
            
            with open(existing_file, 'r') as f:
                existing_data = json.load(f)
            
            # Count before
            before_count = len(existing_data)
            
            # Add new long-form fields that aren't duplicates
            added = 0
            if "long_form_detector" in form_results["fields"] and "fields" in form_results["fields"]["long_form_detector"]:
                for new_field in form_results["fields"]["long_form_detector"]["fields"]:
                    # Check if not already present
                    if not any(f.get("field_label") == new_field["field_label"] for f in existing_data):
                        existing_data.append(new_field)
                        added += 1
            
            # Save enhanced version
            enhanced_file = Path(f"parsed_forms/form_{form_num}_fields_enhanced.json")
            with open(enhanced_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"  ✅ Added {added} new fields to existing {before_count} fields")
            print(f"  📁 Saved to: {enhanced_file}")
            
            form_results["enhancement"] = {
                "before": before_count,
                "added": added,
                "after": len(existing_data)
            }
        
        results[form_num] = form_results
    
    # Save overall results
    results_file = Path("enhanced_parsing_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    
    for form_num, result in results.items():
        if result.get("status") == "not_found":
            print(f"Form {form_num}: NOT FOUND")
        else:
            total_fields = 0
            long_form_count = 0
            
            if "precise_mapper" in result.get("fields", {}):
                pm = result["fields"]["precise_mapper"]
                if "total" in pm:
                    total_fields = pm["total"]
                    long_form_count = len(pm.get("long_form_fields", []))
            
            if "long_form_detector" in result.get("fields", {}):
                lf = result["fields"]["long_form_detector"]
                if "total" in lf:
                    long_form_count = max(long_form_count, lf["total"])
            
            print(f"Form {form_num}: {total_fields} total fields, {long_form_count} long-form fields")
    
    print(f"\n✅ Results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    results = run_enhanced_parsing()