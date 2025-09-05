#!/usr/bin/env python3
"""
GCP Configuration for Enhanced Form Parsing
"""

import os
from pathlib import Path

# GCP Project Configuration
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', '')
GCP_LOCATION = os.environ.get('GCP_LOCATION', 'us')

# Document AI Processor IDs
DOCAI_FORM_PARSER_ID = os.environ.get('DOCAI_FORM_PARSER_ID', '')
DOCAI_OCR_PROCESSOR_ID = os.environ.get('DOCAI_OCR_PROCESSOR_ID', '')

# Credentials
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')

def setup_gcp_auth():
    """
    Setup GCP authentication
    
    To use GCP services:
    1. Create a service account in GCP Console
    2. Download the JSON key file
    3. Set environment variable:
       export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
    4. Set project ID:
       export GCP_PROJECT_ID="your-project-id"
    5. Optional: Create Document AI processors and set IDs:
       export DOCAI_FORM_PARSER_ID="your-form-parser-id"
    """
    
    if not GOOGLE_APPLICATION_CREDENTIALS:
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("To enable GCP features:")
        print("1. Create a GCP service account")
        print("2. Download the JSON key file")
        print("3. Run: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/key.json'")
        return False
    
    if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        print(f"Warning: Credentials file not found: {GOOGLE_APPLICATION_CREDENTIALS}")
        return False
    
    if not GCP_PROJECT_ID:
        print("Warning: GCP_PROJECT_ID not set")
        print("Run: export GCP_PROJECT_ID='your-project-id'")
        return False
    
    print(f"GCP configured for project: {GCP_PROJECT_ID}")
    return True

def is_gcp_available():
    """Check if GCP is properly configured"""
    try:
        from google.cloud import vision
        from google.cloud import documentai
        
        # Check authentication
        if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            return False
        
        if not GCP_PROJECT_ID:
            return False
        
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    if setup_gcp_auth():
        print("GCP authentication configured successfully")
    else:
        print("GCP authentication not configured")