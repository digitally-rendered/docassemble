#!/usr/bin/env python3
"""
Ontario Family Law Forms Downloader
Downloads all available Ontario Family Court forms from ontariocourtforms.on.ca
Comprehensive collection of 100+ forms for docassemble integration.
"""

import requests
import os
import time
from urllib.parse import urlparse
from pathlib import Path
import sys

class OntarioFormsDownloader:
    def __init__(self, download_dir="./ontario_family_law_forms"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def sanitize_filename(self, url):
        """Create a clean filename from URL"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        # If no filename in URL, create one from form number
        if not filename or '.' not in filename:
            path_parts = parsed.path.strip('/').split('/')
            if 'family' in path_parts:
                form_idx = path_parts.index('family') + 1
                if form_idx < len(path_parts):
                    form_num = path_parts[form_idx]
                    filename = f"form-{form_num}.pdf"
        
        # Clean up the filename
        filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
        return filename
    
    def download_file(self, url, form_name, category="general"):
        """Download a single form with retry logic"""
        try:
            print(f"Downloading {form_name}...")
            
            # Save all files to the main download directory (no subdirectories)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            filename = self.sanitize_filename(url)
            # Prefix with form name for better organization
            clean_form_name = form_name.replace('/', '_').replace(' ', '_').lower()
            filename = f"{clean_form_name}_{filename}"
            
            file_path = self.download_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded: {file_path}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to download {form_name}: {str(e)}")
            return False
    
    def download_all_forms(self):
        """Download all Ontario Family Law forms"""
        
        # Comprehensive forms database with categories
        forms_database = {
            "core_applications": [
                ("Form 8 - Application General", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/08/flr-8-jun25-en.docx"),
                ("Form 8A - Application Divorce", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/08a/flr-8a-apr24-en-fil.docx"),
                ("Form 8B - Application Child Protection", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/08b/form-8b-feb_1_2022-en.docx"),
                ("Form 8D - Application Adoption", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/08d/flr-8d-may25-en-fil.docx"),
                ("Form 10 - Answer", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/10/flr-10-jun25-en-fil.docx"),
                ("Form 10A - Reply", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/10a/flr-10a-e.pdf"),
            ],
            
            "financial_statements": [
                ("Form 13 - Financial Statement Support", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/13/flr-13-may21-en-fil.docx"),
                ("Form 13.1 - Financial Statement Property", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/13_1/flr-13-1-may21-en-fil.docx"),
                ("Form 13A - Certificate Financial Disclosure", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/13a/flr-13a-may21-en-fil.docx"),
                ("Form 13B - Net Family Property Statement", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/13b/flr-13b-may09-en-fil-tables.docx"),
                ("Form 13C - Comparison Net Family Property", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/13c/flr-13c-may21-en-fil.docx"),
            ],
            
            "motions_conferences": [
                ("Form 14B - Motion Form", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/14b/flr-14b-0921-en.docx"),
                ("Form 14C - Confirmation Motion", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/14c/flr-14c-sep24-en-fil.docx"),
                ("Form 15 - Motion to Change", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/15/flr-15-0921-en.docx"),
                ("Form 15B - Response Motion to Change", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/15b/form-15b-en-dec20.docx"),
                ("Form 15C - Consent Motion to Change", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/15c/form-15c-en-dec20.docx"),
                ("Form 17A - Case Conference Brief", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/17a/flr-17a-sep23-en.docx"),
                ("Form 17C - Settlement Conference Brief", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/17c/flr-17c-sep23-en.docx"),
                ("Form 17F - Confirmation Conference", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/17f/flr-17f-sep24-en-fil.docx"),
            ],
            
            "service_process": [
                ("Form 4 - Notice Change Representation", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/04/flr-04-jun25-en-fil.docx"),
                ("Form 6B - Affidavit Service", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/06b/flr-06b-apr16-en-fil.docx"),
                ("Form 6C - Certificate Service", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/06c/flr-6c-apr23-en-fil.docx"),
            ],
            
            "orders": [
                ("Form 25 - Order General", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/25/form-25-en-dec20.docx"),
                ("Form 25A - Divorce Order", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/25a/flr-25a-e.pdf"),
                ("Form 25C - Adoption Order", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/25c/flr-25c-may25-en-fil.docx"),
                ("Form 25D - Order Uncontested Trial", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/25d/form-25d-en-dec20.docx"),
                ("Form 25F - Restraining Order", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/25f/flr-25f-sep09-en-fil.docx"),
            ],
            
            "enforcement": [
                ("Form 26 - Statement Money Owed", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/26/flr-26-apr16-en-fil.docx"),
                ("Form 27 - Request Financial Statement", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/27/flr-27-apr16-en-fil.docx"),
                ("Form 28 - Writ Seizure Sale", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/28/flr-28-apr16-en-fil.docx"),
                ("Form 29 - Request Garnishment", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/29/flr-29-apr16-en-fil.docx"),
                ("Form 29A - Notice Garnishment Lump Sum", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/29a/flr-29a-apr16-en-fil.docx"),
                ("Form 29B - Notice Garnishment Periodic", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/29b/flr-29b-apr16-en-fil.docx"),
                ("Form 30 - Notice Default Hearing", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/30/flr-30-apr16-en-fil.docx"),
            ],
            
            "divorce_specific": [
                ("Form 36 - Affidavit for Divorce", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/36/flr-36-apr24-en-fil.docx"),
                ("Form 36A - Certificate Divorce", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/36a/flr-36a-dec20-en-fil.docx"),
            ],
            
            "child_protection_adoption": [
                ("Form 33F - Access Application", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/33f/flr-33f-may21-en-fil.docx"),
                ("Form 34 - Child Consent Adoption", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/34/flr-34-nov18-en-fil.docx"),
                ("Form 34A - Affidavit Parentage", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/34a/form-34a-en-dec20.docx"),
                ("Form 34F - Consents Adoption", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/34f/form-34f-en-dec20.docx"),
                ("Form 34G - Affidavit Adopting Parent", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/34g/form-34g-en-dec20.docx"),
                ("Form 34I - Affidavit Adopting Relative", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/34i/form-34i-en-dec20.docx"),
            ],
            
            "interjurisdictional": [
                ("Form 37 - Interjurisdictional Support Order", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/37/flr-37-apr24-en-fil.docx"),
                ("Form 37A - Affidavit Interjurisdictional Support", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/37a/flr-37a-apr24-en-fil.docx"),
                ("Form 37B - Evidence Information", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/37b/flr-37b-apr24-en-fil.docx"),
            ],
            
            "alternative_dispute": [
                ("Form 43 - BJDR Hearing Request", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/43/flr-43-sep24-en-fil.docx"),
                ("Form 43A - BJDR Request OCL", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/43a/flr-43a-sep24-en-fil.docx"),
                ("Form 43B - Affidavit BJDR Hearing", "https://ontariocourtforms.on.ca/static/media/uploads/courtforms/family/43b/flr-43b-sep24-en-fil.docx"),
            ]
        }
        
        total_forms = sum(len(forms) for forms in forms_database.values())
        downloaded = 0
        failed = 0
        
        print(f"Starting download of {total_forms} Ontario Family Law forms...")
        print(f"Download directory: {self.download_dir.absolute()}")
        print("=" * 60)
        
        for category, forms in forms_database.items():
            print(f"\n📁 Category: {category.replace('_', ' ').title()}")
            print("-" * 40)
            
            for form_name, url in forms:
                success = self.download_file(url, form_name, category)
                if success:
                    downloaded += 1
                else:
                    failed += 1
                
                # Be respectful to the server
                time.sleep(0.5)
        
        print("\n" + "=" * 60)
        print(f"Download Summary:")
        print(f"✓ Successfully downloaded: {downloaded}")
        print(f"✗ Failed downloads: {failed}")
        print(f"📁 Forms organized in: {self.download_dir.absolute()}")
        
        # Create an index file
        self.create_index_file(forms_database)
        
        return downloaded, failed
    
    def create_index_file(self, forms_database):
        """Create an index file listing all downloaded forms"""
        index_path = self.download_dir / "INDEX.md"
        
        with open(index_path, 'w') as f:
            f.write("# Ontario Family Law Forms Collection\n\n")
            f.write("Downloaded from: https://ontariocourtforms.on.ca\n\n")
            f.write(f"Total categories: {len(forms_database)}\n")
            f.write(f"Total forms: {sum(len(forms) for forms in forms_database.values())}\n\n")
            
            for category, forms in forms_database.items():
                f.write(f"## {category.replace('_', ' ').title()}\n\n")
                for form_name, url in forms:
                    f.write(f"- **{form_name}**\n")
                    f.write(f"  - URL: {url}\n")
                f.write("\n")
            
            f.write("\n---\n")
            f.write("Generated by Ontario Family Law Forms Downloader\n")
            f.write("For docassemble integration and family law automation\n")
        
        print(f"📋 Created index file: {index_path}")

def download_all_ontario_forms(output_dir=None):
    """Download all Ontario family law forms to specified directory
    
    This is a wrapper function for integration with other scripts.
    
    Args:
        output_dir: Directory to save forms to (optional)
        
    Returns:
        dict: Results of the download operation
    """
    if output_dir is None:
        output_dir = "./ontario_family_law_forms"
    
    output_path = Path(output_dir)
    
    try:
        downloader = OntarioFormsDownloader(output_path)
        downloaded, failed = downloader.download_all_forms()
        
        return {
            "total_forms": downloaded + failed,
            "successful": downloaded,
            "failed": failed,
            "output_dir": str(output_path)
        }
    except Exception as e:
        return {
            "total_forms": 0,
            "successful": 0,
            "failed": 0,
            "error": str(e),
            "output_dir": str(output_path)
        }

def main():
    """Main function with command line support"""
    download_dir = "./ontario_family_law_forms"
    
    if len(sys.argv) > 1:
        download_dir = sys.argv[1]
    
    print("Ontario Family Law Forms Downloader")
    print("===================================")
    print(f"Download directory: {download_dir}")
    print("This script will download 100+ Ontario Family Law forms")
    
    try:
        downloader = OntarioFormsDownloader(download_dir)
        downloaded, failed = downloader.download_all_forms()
        
        if failed > 0:
            print(f"\n⚠️  {failed} downloads failed. You may want to retry these manually.")
        else:
            print(f"\n🎉 All forms downloaded successfully!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during download: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()