#!/usr/bin/env python3
"""
Simple test to isolate the generation error
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    print("Testing imports...")
    from common_interview_generator import CommonInterviewGenerator
    print("✅ CommonInterviewGenerator imported")
    
    generator = CommonInterviewGenerator()
    print("✅ Generator initialized")
    
    print("Testing form config...")
    config = generator.form_configs.get("8", {})
    print(f"✅ Got config: {config}")
    
    print("Testing interview generation...")
    interview = generator.generate_interview("8")
    print(f"✅ Generated interview with {len(interview.sections)} sections")
    
    print("Testing YAML generation...")
    yaml_content = interview.to_yaml()
    print(f"✅ Generated YAML: {len(yaml_content)} characters")
    
    print("SUCCESS: All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()