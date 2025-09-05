#!/usr/bin/env python3
"""
Setup GCP Document AI Processors for Ontario Form Parsing
"""

import os
import json
import time
from google.cloud import documentai_v1 as documentai
from google.api_core import operations_v1

# Set project configuration
PROJECT_ID = "default-456005"
LOCATION = "us"  # Document AI is available in us or eu

os.environ['GCP_PROJECT_ID'] = PROJECT_ID

def create_processor(display_name: str, processor_type: str):
    """Create a Document AI processor"""
    
    # Create client
    client = documentai.DocumentProcessorServiceClient()
    
    # The full resource name of the location
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    
    # Create processor
    processor = documentai.Processor(
        display_name=display_name,
        type_=processor_type
    )
    
    try:
        # Create the processor
        operation = client.create_processor(
            parent=parent,
            processor=processor
        )
        
        print(f"Creating processor: {display_name}")
        print(f"Type: {processor_type}")
        
        # Wait for operation to complete
        print("Waiting for operation to complete", end="")
        result = operation.result(timeout=300)  # 5 minute timeout
        
        print("\n✅ Processor created successfully!")
        print(f"Processor name: {result.name}")
        
        # Extract processor ID
        processor_id = result.name.split('/processors/')[-1]
        print(f"Processor ID: {processor_id}")
        return processor_id
            
    except Exception as e:
        print(f"\n❌ Error creating processor: {e}")
        if "already exists" in str(e):
            print("Processor may already exist. Listing existing processors...")
            list_processors()
    
    return None

def list_processors():
    """List existing Document AI processors"""
    client = documentai.DocumentProcessorServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    
    try:
        processors = client.list_processors(parent=parent)
        
        print("\n📋 Existing processors:")
        processor_info = []
        
        for processor in processors:
            print(f"  - {processor.display_name}")
            print(f"    Type: {processor.type_}")
            print(f"    ID: {processor.name.split('/')[-1]}")
            print(f"    State: {processor.state}")
            
            processor_info.append({
                'display_name': processor.display_name,
                'type': processor.type_,
                'id': processor.name.split('/')[-1],
                'full_name': processor.name
            })
        
        # Save processor info
        with open('gcp_processors.json', 'w') as f:
            json.dump(processor_info, f, indent=2)
        
        print(f"\n💾 Processor info saved to gcp_processors.json")
        
        return processor_info
        
    except Exception as e:
        print(f"Error listing processors: {e}")
        return []

def setup_processors():
    """Setup all required processors for Ontario form parsing"""
    
    print("=" * 60)
    print("SETTING UP GCP DOCUMENT AI PROCESSORS")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print()
    
    # List of processors to create
    processors_to_create = [
        {
            'display_name': 'Ontario Form Parser',
            'type': 'FORM_PARSER_PROCESSOR'
        },
        {
            'display_name': 'Ontario OCR Processor',
            'type': 'OCR_PROCESSOR'
        }
    ]
    
    created_processors = {}
    
    # First, list existing processors
    existing = list_processors()
    
    # Check what we need to create
    for proc_config in processors_to_create:
        exists = False
        for existing_proc in existing:
            if existing_proc['type'] == proc_config['type']:
                print(f"\n✅ {proc_config['display_name']} already exists")
                print(f"   ID: {existing_proc['id']}")
                created_processors[proc_config['type']] = existing_proc['id']
                exists = True
                break
        
        if not exists:
            print(f"\n🔧 Creating {proc_config['display_name']}...")
            processor_id = create_processor(
                proc_config['display_name'],
                proc_config['type']
            )
            if processor_id:
                created_processors[proc_config['type']] = processor_id
    
    # Save environment configuration
    env_config = f"""
# GCP Configuration for Ontario Form Parsing
export GCP_PROJECT_ID="{PROJECT_ID}"
export GCP_LOCATION="{LOCATION}"
"""
    
    if 'FORM_PARSER_PROCESSOR' in created_processors:
        env_config += f'export DOCAI_FORM_PARSER_ID="{created_processors["FORM_PARSER_PROCESSOR"]}"\n'
    
    if 'OCR_PROCESSOR' in created_processors:
        env_config += f'export DOCAI_OCR_PROCESSOR_ID="{created_processors["OCR_PROCESSOR"]}"\n'
    
    with open('gcp_env_config.sh', 'w') as f:
        f.write(env_config)
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo use these processors, run:")
    print("  source gcp_env_config.sh")
    print("\nOr add these to your environment:")
    print(env_config)

if __name__ == "__main__":
    setup_processors()