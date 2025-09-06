#!/usr/bin/env python3
"""
Run Enhanced Generation - Main executable for the enhanced Ontario family law form generator
Demonstrates the complete common interview framework integration
"""

import sys
import logging
import argparse
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_form_integration import EnhancedFormIntegrator
from common_interview_generator import CommonInterviewGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_generation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Enhanced Ontario Family Law Form Generator         ║
║                                                              ║
║  🏛️  Ontario Superior Court of Justice Forms                ║
║  🤖  Programmatic YAML Object Generation                     ║
║  ♻️  Integrates Existing Parsing Infrastructure              ║
║  ✅  Common Interview Components                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def print_system_overview():
    """Print system overview"""
    print("""
📋 SYSTEM OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ KEEPS (Existing Infrastructure):
   📁 automated_form_processor.py    - Form processing workflow
   📁 field_validation_mapper.py     - Field validation and mapping
   📁 comprehensive_form_parser.py   - PDF/DOCX parsing with Google Cloud
   📁 parsed_forms/*.json           - All parsed field data (26+ forms)
   📁 ontario_forms_registry.json   - Form metadata registry

🆕 ADDS (New Generation System):
   📁 ontario_common_fields.py       - Common field definitions & validation
   📁 ontario_party_objects.py       - Person/organization dataclasses
   📁 ontario_court_objects.py       - Court and case information objects
   📁 ontario_children_objects.py    - Children and family structure objects
   📁 ontario_financial_objects.py   - Financial statement components
   📁 common_interview_generator.py  - Main code generation engine
   📁 enhanced_form_integration.py   - Integration orchestrator

🎯 RESULT:
   ✨ Clean YAML object generation (no string concatenation!)
   🔗 Reusable components across all forms
   🎨 Demo pattern integration
   🛡️ Error handling and validation
   📊 Comprehensive test generation
    """)

def demonstrate_common_components():
    """Demonstrate common components functionality"""
    print("""
🧩 COMMON COMPONENTS DEMONSTRATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    # Import components
    from ontario_common_fields import ontario_common_fields
    from ontario_party_objects import ontario_party_generator
    from ontario_court_objects import ontario_court_generator
    from ontario_children_objects import ontario_children_generator
    from ontario_financial_objects import ontario_financial_generator
    
    # Demonstrate common fields
    print("1. 📝 COMMON FIELDS:")
    party_fields = ontario_common_fields.get_fields_by_category("party")
    print(f"   Found {len(party_fields)} common party fields:")
    for field in party_fields[:3]:  # Show first 3
        print(f"   • {field.field_name}: {field.label}")
    
    # Demonstrate party objects
    print("\n2. 👥 PARTY OBJECTS:")
    party_objects = ontario_party_generator.generate_party_objects()
    print(f"   Generated {len(party_objects)} party objects:")
    for obj in party_objects[:3]:  # Show first 3
        print(f"   • {list(obj.keys())[0]}: {list(obj.values())[0]}")
    
    # Demonstrate court objects
    print("\n3. 🏛️ COURT OBJECTS:")
    court_questions = ontario_court_generator.generate_court_questions()
    print(f"   Generated {len(court_questions)} court questions")
    
    # Demonstrate children objects  
    print("\n4. 👨‍👩‍👧‍👦 CHILDREN OBJECTS:")
    children_objects = ontario_children_generator.generate_children_objects()
    print(f"   Generated {len(children_objects)} children objects:")
    for obj in children_objects:
        print(f"   • {list(obj.keys())[0]}: {list(obj.values())[0]}")
    
    # Demonstrate financial objects
    print("\n5. 💰 FINANCIAL OBJECTS:")
    financial_objects = ontario_financial_generator.generate_financial_objects()
    print(f"   Generated {len(financial_objects)} financial objects:")
    for obj in financial_objects[:3]:  # Show first 3
        print(f"   • {list(obj.keys())[0]}: {list(obj.values())[0]}")

def generate_sample_interview():
    """Generate and display a sample interview"""
    print("""
🎯 SAMPLE INTERVIEW GENERATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    generator = CommonInterviewGenerator()
    
    # Generate Form 8 (Application General) as example
    print("Generating Ontario Form 8 - Application (General)...")
    
    try:
        interview = generator.generate_interview("8")
        
        print(f"✅ Generated interview with {len(interview.sections)} sections:")
        for section in interview.sections:
            print(f"   • {section.title} ({len(section.yaml_objects)} objects)")
        
        # Show first few lines of generated YAML
        yaml_content = interview.to_yaml()
        yaml_lines = yaml_content.split('\n')[:20]
        
        print(f"\n📄 First 20 lines of generated YAML:")
        print("   " + "\n   ".join(yaml_lines))
        print("   ...")
        print(f"   [Total: {len(yaml_content.split())} lines]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating sample interview: {e}")
        return False

def run_enhanced_generation(form_number: str = None, all_forms: bool = False):
    """Run the enhanced generation process"""
    print("""
🚀 ENHANCED GENERATION PROCESS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    integrator = EnhancedFormIntegrator()
    
    if form_number:
        # Generate single form
        print(f"Generating enhanced interview for Form {form_number}...")
        try:
            result = integrator.generate_enhanced_interview(form_number)
            print(f"✅ Success! Generated Form {form_number}")
            print(f"   📄 Title: {result.form_title}")
            print(f"   📊 Parsed Fields: {result.parsed_fields_count}")
            print(f"   🎯 Validation Score: {result.validation_score:.2f}")
            print(f"   ⏱️ Processing Time: {result.processing_time:.2f}s")
            print(f"   📁 Output: {Path(result.generated_file_path).name}")
            return [result]
            
        except Exception as e:
            print(f"❌ Error generating Form {form_number}: {e}")
            return []
    
    elif all_forms:
        # Generate all forms
        print("Generating enhanced interviews for all forms...")
        results = integrator.generate_all_enhanced_interviews()
        
        if results:
            print(f"✅ Successfully generated {len(results)} form interviews!")
            
            # Show summary
            total_fields = sum(r.parsed_fields_count for r in results.values())
            avg_validation = sum(r.validation_score for r in results.values()) / len(results)
            total_time = sum(r.processing_time for r in results.values())
            
            print(f"   📊 Total Parsed Fields: {total_fields:,}")
            print(f"   🎯 Average Validation Score: {avg_validation:.2f}")
            print(f"   ⏱️ Total Processing Time: {total_time:.2f}s")
            
            # Generate and save report
            report = integrator.generate_processing_report(results)
            report_file = Path(__file__).parent / "generated_interviews" / "processing_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"   📄 Report saved: {report_file.name}")
            
            return list(results.values())
        else:
            print("❌ No forms were successfully generated")
            return []
    
    else:
        print("No generation option selected. Use --form or --all")
        return []

def show_generated_files():
    """Show generated files"""
    print("""
📁 GENERATED FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    generated_dir = Path(__file__).parent / "generated_interviews"
    
    if generated_dir.exists():
        yml_files = list(generated_dir.glob("*.yml"))
        txt_files = list(generated_dir.glob("*.txt"))
        
        print(f"📂 Directory: {generated_dir}")
        print(f"📄 Interview Files: {len(yml_files)}")
        print(f"📄 Report Files: {len(txt_files)}")
        print()
        
        # Show YAML files
        if yml_files:
            print("🎯 Generated Interview Files:")
            for file_path in sorted(yml_files):
                file_size = file_path.stat().st_size
                print(f"   • {file_path.name} ({file_size:,} bytes)")
        
        # Show report files
        if txt_files:
            print("\n📊 Report Files:")
            for file_path in sorted(txt_files):
                print(f"   • {file_path.name}")
        
        return len(yml_files) + len(txt_files)
    else:
        print("📂 No generated files directory found")
        print("   Run generation first with --form or --all")
        return 0

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Enhanced Ontario Family Law Form Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--form", "-f", 
                       help="Generate enhanced interview for specific form (e.g., 8, 13, 15)")
    
    parser.add_argument("--all", "-a", action="store_true",
                       help="Generate enhanced interviews for all forms")
    
    parser.add_argument("--demo", "-d", action="store_true",
                       help="Show demonstration of common components")
    
    parser.add_argument("--sample", "-s", action="store_true", 
                       help="Generate and show sample interview")
    
    parser.add_argument("--files", action="store_true",
                       help="Show generated files")
    
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Quiet mode - less output")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Print banner unless quiet
    if not args.quiet:
        print_banner()
        print_system_overview()
    
    # Handle commands
    if args.demo:
        demonstrate_common_components()
    
    if args.sample:
        generate_sample_interview()
    
    if args.form or args.all:
        results = run_enhanced_generation(args.form, args.all)
        
        if results and not args.quiet:
            print(f"\n🎉 Generation completed successfully!")
            print(f"📁 Check 'generated_interviews' directory for output files")
    
    if args.files:
        file_count = show_generated_files()
        if file_count > 0:
            print(f"\n✅ Found {file_count} generated files")
    
    # Default behavior if no args
    if not any([args.form, args.all, args.demo, args.sample, args.files]):
        if not args.quiet:
            print("""
🚀 GETTING STARTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Available commands:
  
  python run_enhanced_generation.py --demo          # Show component demo
  python run_enhanced_generation.py --sample        # Generate sample interview  
  python run_enhanced_generation.py --form 8        # Generate Form 8
  python run_enhanced_generation.py --all           # Generate all forms
  python run_enhanced_generation.py --files         # Show generated files
  
  python run_enhanced_generation.py --help          # Show all options

Example workflow:
  1. python run_enhanced_generation.py --demo       # See what's available
  2. python run_enhanced_generation.py --sample     # Try sample generation
  3. python run_enhanced_generation.py --all        # Generate all forms
  4. python run_enhanced_generation.py --files      # Check output
            """)

if __name__ == "__main__":
    main()