#!/usr/bin/env python3
"""
Enhanced Long-Form Text Field Detector for Ontario Family Law Forms
Specifically designed to detect narrative/paragraph text areas that other parsers miss
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import PyPDF2
import pdfplumber
from dataclasses import dataclass, field
import fitz  # PyMuPDF


@dataclass
class LongFormField:
    """Represents a long-form text field in a legal form"""
    field_id: str
    section: str
    label: str
    prompt: str
    estimated_lines: int = 5
    required: bool = False
    page_number: int = 1
    field_type: str = "area"  # Docassemble 'area' for multiline text
    context_before: str = ""
    context_after: str = ""
    

class LongFormFieldDetector:
    """Specialized detector for narrative/long-form text fields in legal forms"""
    
    # Patterns that indicate a long-form text field
    LONG_FORM_INDICATORS = [
        # Direct prompts for narrative
        r"describe\s+(?:the\s+)?(?:facts?|circumstances?|details?|reasons?)",
        r"explain\s+(?:why|how|what|the\s+reasons?)",
        r"provide\s+(?:details?|information|facts?|evidence)",
        r"list\s+(?:all\s+)?(?:the\s+)?(?:reasons?|grounds?|facts?)",
        r"state\s+(?:the\s+)?(?:reasons?|grounds?|facts?|basis)",
        r"set\s+out\s+(?:the\s+)?(?:facts?|details?|grounds?)",
        r"give\s+(?:details?|reasons?|information)",
        r"specify\s+(?:the\s+)?(?:grounds?|reasons?|details?)",
        r"outline\s+(?:the\s+)?(?:facts?|circumstances?|details?)",
        
        # Legal terminology
        r"grounds?\s+(?:for|of)\s+(?:the\s+)?(?:application|claim|motion|divorce)",
        r"facts?\s+(?:supporting|relied\s+upon|in\s+support)",
        r"legal\s+basis\s+(?:for|of)",
        r"relief\s+sought",
        r"claims?\s+(?:made|sought|requested)",
        r"particulars?\s+of",
        r"allegations?",
        r"evidence\s+(?:of|supporting)",
        r"history\s+of\s+(?:the\s+)?(?:relationship|marriage|proceedings)",
        r"chronology\s+of\s+events?",
        
        # Form-specific sections
        r"additional\s+information",
        r"other\s+(?:orders?|relief|claims?)",
        r"further\s+details?",
        r"comments?",
        r"notes?",
        r"narrative",
        r"statement\s+of\s+facts?",
        r"affidavit\s+(?:evidence|statement)",
        r"sworn\s+statement",
        
        # Instructions that precede long-form fields
        r"in\s+the\s+space\s+(?:below|provided)",
        r"use\s+(?:the\s+)?(?:space\s+)?(?:below|additional\s+pages?)",
        r"attach\s+(?:additional\s+)?(?:pages?|sheets?)\s+if\s+(?:needed|necessary)",
        r"continue\s+on\s+(?:additional|separate)\s+(?:page|sheet)",
        r"if\s+more\s+space\s+is\s+needed",
        r"write\s+your\s+(?:answer|response|statement)",
    ]
    
    # Patterns for specific form sections
    FORM_SPECIFIC_SECTIONS = {
        "8": [  # Form 8 - Application (General)
            "The applicant claims:",
            "The grounds for the application are:",
            "Facts relied upon:",
            "Children - provide details:",
            "Previous court cases:",
            "Urgency - explain why urgent:",
            "Other orders sought:"
        ],
        "8A": [  # Form 8A - Application (Divorce)
            "Grounds for divorce:",
            "Marriage breakdown details:",
            "Separation circumstances:",
            "Reconciliation attempts:",
            "Adultery details (if applicable):",
            "Cruelty details (if applicable):",
            "Collusion, connivance or condonation:"
        ],
        "10": [  # Form 10 - Answer
            "Response to applicant's claims:",
            "Dispute the following:",
            "Additional facts:",
            "Different version of events:",
            "Counterclaim details:",
            "Relief sought by respondent:"
        ],
        "36": [  # Form 36 - Affidavit for Divorce
            "Marriage history:",
            "Grounds for divorce - details:",
            "Children arrangements:",
            "Support arrangements:",
            "Property arrangements:",
            "Barriers to remarriage:",
            "Other relevant information:"
        ],
        "17A": [  # Form 17A - Case Conference Brief  
            "Issues for conference:",
            "Facts in dispute:",
            "Proposals for settlement:",
            "Financial disclosure:",
            "Witnesses and evidence:"
        ],
        "17C": [  # Form 17C - Settlement Conference Brief
            "Settlement position:",
            "Outstanding issues:",
            "Offers to settle:",
            "Admissions:",
            "Trial estimate and witnesses:"
        ]
    }
    
    def __init__(self):
        self.detected_fields = []
        self.form_number = None
        
    def detect_long_form_fields(self, pdf_path: str, form_number: str = None) -> List[LongFormField]:
        """Main detection method combining multiple strategies"""
        
        self.form_number = form_number or self._extract_form_number(pdf_path)
        self.detected_fields = []
        
        # Strategy 1: Pattern-based detection
        self._detect_by_patterns(pdf_path)
        
        # Strategy 2: Form-specific section detection
        if self.form_number:
            self._detect_form_specific_sections(pdf_path)
        
        # Strategy 3: Visual/spatial detection (lines for writing)
        self._detect_by_visual_cues(pdf_path)
        
        # Strategy 4: Instruction-based detection
        self._detect_by_instructions(pdf_path)
        
        # Deduplicate and merge results
        return self._merge_and_deduplicate()
    
    def _detect_by_patterns(self, pdf_path: str):
        """Detect using regex patterns for long-form indicators"""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    
                    # Split into lines for context
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines):
                        line_lower = line.lower().strip()
                        
                        # Check each pattern
                        for pattern in self.LONG_FORM_INDICATORS:
                            if re.search(pattern, line_lower):
                                # Get context
                                context_before = lines[i-1] if i > 0 else ""
                                context_after = lines[i+1] if i < len(lines)-1 else ""
                                
                                # Look for writing space after the prompt
                                has_space = self._check_for_writing_space(page, i, lines)
                                
                                if has_space:
                                    field = LongFormField(
                                        field_id=f"long_form_{page_num}_{i}",
                                        section=self._extract_section(context_before),
                                        label=line.strip(),
                                        prompt=line.strip(),
                                        page_number=page_num,
                                        context_before=context_before,
                                        context_after=context_after,
                                        estimated_lines=self._estimate_lines(page, i)
                                    )
                                    self.detected_fields.append(field)
                                    break
                                    
        except Exception as e:
            print(f"Error in pattern detection: {e}")
    
    def _detect_form_specific_sections(self, pdf_path: str):
        """Detect sections specific to known forms"""
        
        if self.form_number not in self.FORM_SPECIFIC_SECTIONS:
            return
            
        sections = self.FORM_SPECIFIC_SECTIONS[self.form_number]
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                page_map = {}
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    start_pos = len(full_text)
                    full_text += page_text + "\n"
                    
                    # Map character positions to pages
                    for i in range(start_pos, len(full_text)):
                        page_map[i] = page_num
                
                # Search for each known section
                for section_prompt in sections:
                    # Flexible matching
                    pattern = re.escape(section_prompt).replace(r'\:', r':?\s*')
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    
                    for match in matches:
                        pos = match.start()
                        page_num = page_map.get(pos, 1)
                        
                        field = LongFormField(
                            field_id=f"form{self.form_number}_section_{section_prompt[:20]}",
                            section=section_prompt,
                            label=section_prompt,
                            prompt=match.group(),
                            page_number=page_num,
                            required=True,  # Form-specific sections usually required
                            estimated_lines=10  # Assume substantial space needed
                        )
                        self.detected_fields.append(field)
                        
        except Exception as e:
            print(f"Error in form-specific detection: {e}")
    
    def _detect_by_visual_cues(self, pdf_path: str):
        """Detect by looking for visual writing spaces (lines, boxes)"""
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                # Look for horizontal lines that indicate writing space
                drawings = page.get_drawings()
                
                # Group horizontal lines
                horizontal_lines = []
                for drawing in drawings:
                    for item in drawing.get("items", []):
                        if item[0] == "l":  # Line
                            p1, p2 = item[1], item[2]
                            # Check if horizontal (y coords similar)
                            if abs(p1.y - p2.y) < 2:
                                horizontal_lines.append((p1.y, p2.x - p1.x))
                
                # Look for multiple parallel lines (indicates text area)
                line_groups = self._group_parallel_lines(horizontal_lines)
                
                for group in line_groups:
                    if len(group) >= 3:  # At least 3 lines suggests text area
                        # Find text above the lines (the prompt)
                        prompt_text = self._find_text_above_lines(page, group[0][0])
                        
                        if prompt_text:
                            field = LongFormField(
                                field_id=f"visual_{page_num}_{int(group[0][0])}",
                                section="",
                                label=prompt_text,
                                prompt=prompt_text,
                                page_number=page_num,
                                estimated_lines=len(group)
                            )
                            self.detected_fields.append(field)
                            
            doc.close()
            
        except Exception as e:
            print(f"Error in visual detection: {e}")
    
    def _detect_by_instructions(self, pdf_path: str):
        """Detect by looking for instructions about providing information"""
        
        instructions = [
            r"(?:provide|give|state|describe|explain|list)\s+(?:the\s+)?following",
            r"complete\s+this\s+section",
            r"fill\s+in\s+(?:the\s+)?(?:details?|information)",
            r"answer\s+(?:the\s+)?(?:following|questions?)",
            r"respond\s+to\s+(?:each|the)",
        ]
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    
                    for pattern in instructions:
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        for match in matches:
                            # Extract the section this instruction relates to
                            context = text[max(0, match.start()-100):match.end()+200]
                            
                            field = LongFormField(
                                field_id=f"instruction_{page_num}_{match.start()}",
                                section=self._extract_section(context),
                                label=match.group(),
                                prompt=match.group(),
                                page_number=page_num,
                                estimated_lines=5
                            )
                            self.detected_fields.append(field)
                            
        except Exception as e:
            print(f"Error in instruction detection: {e}")
    
    def _check_for_writing_space(self, page, line_index: int, lines: List[str]) -> bool:
        """Check if there's space for writing after a prompt"""
        
        # Simple heuristic: look for empty lines or lines with just underscores
        if line_index < len(lines) - 1:
            next_lines = lines[line_index+1:min(line_index+5, len(lines))]
            
            empty_count = 0
            for line in next_lines:
                stripped = line.strip()
                if not stripped or stripped == "_" * len(stripped) or stripped == "." * len(stripped):
                    empty_count += 1
            
            return empty_count >= 2
        
        return False
    
    def _estimate_lines(self, page, line_index: int) -> int:
        """Estimate how many lines of text space are provided"""
        # This would need visual analysis to be accurate
        # For now, use heuristics
        return 5  # Default estimate
    
    def _extract_section(self, text: str) -> str:
        """Extract section heading from context"""
        # Look for numbered sections or headings
        section_match = re.search(r"(?:^|\n)(\d+\.?\s+[A-Z][^.]+)", text)
        if section_match:
            return section_match.group(1).strip()
        return ""
    
    def _group_parallel_lines(self, lines: List[Tuple[float, float]]) -> List[List[Tuple[float, float]]]:
        """Group horizontal lines that are parallel and evenly spaced"""
        if not lines:
            return []
        
        # Sort by y-coordinate
        lines.sort(key=lambda x: x[0])
        
        groups = []
        current_group = [lines[0]]
        
        for i in range(1, len(lines)):
            y_diff = lines[i][0] - lines[i-1][0]
            # If lines are evenly spaced (within tolerance)
            if 15 < y_diff < 30:  # Typical line spacing
                current_group.append(lines[i])
            else:
                if len(current_group) >= 3:
                    groups.append(current_group)
                current_group = [lines[i]]
        
        if len(current_group) >= 3:
            groups.append(current_group)
        
        return groups
    
    def _find_text_above_lines(self, page, y_coord: float) -> str:
        """Find text just above a set of lines"""
        text_instances = page.get_text("dict")
        
        for block in text_instances.get("blocks", []):
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # If text is just above the lines
                        if span["bbox"][3] < y_coord and y_coord - span["bbox"][3] < 20:
                            return span.get("text", "").strip()
        
        return ""
    
    def _extract_form_number(self, pdf_path: str) -> Optional[str]:
        """Extract form number from filename or content"""
        filename = Path(pdf_path).stem.lower()
        
        # Try to extract from filename
        match = re.search(r'form[_\s-]?(\d+[a-z]?)', filename)
        if match:
            return match.group(1).upper()
        
        return None
    
    def _merge_and_deduplicate(self) -> List[LongFormField]:
        """Merge and deduplicate detected fields"""
        
        # Group similar fields
        unique_fields = {}
        
        for field in self.detected_fields:
            # Create a key for grouping
            key = (field.page_number, field.label[:30])
            
            if key not in unique_fields:
                unique_fields[key] = field
            else:
                # Merge information
                existing = unique_fields[key]
                existing.estimated_lines = max(existing.estimated_lines, field.estimated_lines)
                if not existing.section and field.section:
                    existing.section = field.section
        
        return list(unique_fields.values())
    

def enhance_form_parsing(form_number: str, pdf_path: str = None) -> Dict:
    """Enhanced parsing that includes long-form field detection"""
    
    detector = LongFormFieldDetector()
    
    # If no PDF path provided, try to find it
    if not pdf_path:
        pdf_path = f"ontario_forms/form_{form_number}.pdf"
    
    if not Path(pdf_path).exists():
        print(f"Warning: PDF not found at {pdf_path}")
        return {"error": "PDF not found", "fields": []}
    
    # Detect long-form fields
    long_form_fields = detector.detect_long_form_fields(pdf_path, form_number)
    
    # Convert to standard format
    enhanced_fields = []
    for lf_field in long_form_fields:
        enhanced_fields.append({
            "field_id": lf_field.field_id,
            "field_name": re.sub(r'[^a-z0-9_]', '_', lf_field.label.lower())[:50],
            "field_type": "area",  # Docassemble multiline text
            "field_label": lf_field.label,
            "required": lf_field.required,
            "section": lf_field.section,
            "prompt": lf_field.prompt,
            "estimated_lines": lf_field.estimated_lines,
            "page_number": lf_field.page_number,
            "detection_method": "long_form_detector"
        })
    
    return {
        "form_number": form_number,
        "long_form_fields": enhanced_fields,
        "total_detected": len(enhanced_fields)
    }


def update_existing_parsed_data(form_number: str):
    """Update existing parsed data with long-form fields"""
    
    # Load existing parsed data
    parsed_file = Path(f"parsed_forms/form_{form_number}_fields.json")
    
    if parsed_file.exists():
        with open(parsed_file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    # Get long-form fields
    enhanced = enhance_form_parsing(form_number)
    
    if enhanced.get("long_form_fields"):
        # Add to existing data
        for field in enhanced["long_form_fields"]:
            # Check if not already present
            if not any(e.get("field_label") == field["field_label"] for e in existing_data):
                existing_data.append(field)
        
        # Save updated data
        output_file = Path(f"parsed_forms/form_{form_number}_fields_enhanced.json")
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"✅ Added {len(enhanced['long_form_fields'])} long-form fields to Form {form_number}")
        print(f"📁 Saved to: {output_file}")
        
        return existing_data
    
    return existing_data


if __name__ == "__main__":
    # Test on forms known to have long-form fields
    test_forms = ["8", "8A", "10", "36", "17A", "17C", "13A", "29A", "29B", "33F", "36A"]
    
    results = {}
    for form_num in test_forms:
        print(f"\n🔍 Detecting long-form fields in Form {form_num}...")
        result = enhance_form_parsing(form_num)
        results[form_num] = result
        
        if result.get("long_form_fields"):
            print(f"Found {len(result['long_form_fields'])} long-form fields:")
            for field in result["long_form_fields"][:3]:  # Show first 3
                print(f"  - {field['field_label'][:50]}...")
    
    # Save results
    with open("long_form_detection_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n📊 Summary:")
    for form_num, result in results.items():
        count = result.get("total_detected", 0)
        print(f"  Form {form_num}: {count} long-form fields detected")