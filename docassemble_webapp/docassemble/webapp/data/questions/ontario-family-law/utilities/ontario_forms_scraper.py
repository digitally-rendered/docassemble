#!/usr/bin/env python3
"""
Ontario Court Forms Website Scraper
Automatically extracts all family law forms information from the official website
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Tuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntarioFormsScraper:
    """Scrapes all family law forms from Ontario Court Forms website"""
    
    def __init__(self):
        self.base_url = "https://ontariocourtforms.on.ca"
        self.forms_url = f"{self.base_url}/en/family-law-rules-forms/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def scrape_all_forms(self) -> List[Dict]:
        """Scrape all forms information from the website"""
        logger.info(f"Scraping forms from {self.forms_url}")
        
        response = self.session.get(self.forms_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        forms = []
        
        # Find all form links - they typically have patterns like /family/08/, /family/13/, etc.
        form_links = soup.find_all('a', href=re.compile(r'/family/\d+[a-z]?/?'))
        
        logger.info(f"Found {len(form_links)} form links to process")
        
        for link in form_links:
            try:
                form_info = self.extract_form_info(link)
                if form_info:
                    forms.append(form_info)
                    logger.info(f"Extracted: Form {form_info['form_number']} - {form_info['form_title']}")
            except Exception as e:
                logger.error(f"Error processing form link: {e}")
                
        # Also look for forms in tables or lists
        forms.extend(self.extract_forms_from_tables(soup))
        
        # Remove duplicates based on form number
        unique_forms = {}
        for form in forms:
            if form['form_number'] not in unique_forms:
                unique_forms[form['form_number']] = form
                
        return list(unique_forms.values())
    
    def extract_form_info(self, link_element) -> Dict:
        """Extract form information from a link element"""
        href = link_element.get('href', '')
        text = link_element.get_text(strip=True)
        
        # Extract form number from URL or text
        form_number = self.extract_form_number(href, text)
        if not form_number:
            return None
            
        # Extract form title
        form_title = self.clean_form_title(text)
        
        # Determine form URL
        if href.startswith('http'):
            form_url = href
        else:
            form_url = f"{self.base_url}{href}"
            
        # Get form details page if available
        form_details = self.get_form_details(form_url)
        
        return {
            'form_number': form_number,
            'form_title': form_title,
            'form_url': form_url,
            'form_type': self.determine_form_type(form_title),
            'category': self.determine_category(form_title, form_number),
            'download_links': form_details.get('download_links', {}),
            'description': form_details.get('description', ''),
            'has_children_section': self.check_children_section(form_title, form_number),
            'requires_financial': self.check_financial_requirement(form_number),
            'has_property_section': self.check_property_section(form_number)
        }
    
    def extract_forms_from_tables(self, soup) -> List[Dict]:
        """Extract forms from tables on the page"""
        forms = []
        
        # Look for tables with form information
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Look for form number patterns
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        if re.search(r'Form\s+\d+[A-Z]?\.?\d*', text):
                            form_number = self.extract_form_number('', text)
                            if form_number:
                                # Find download links in the row
                                links = row.find_all('a', href=True)
                                download_links = {}
                                for link in links:
                                    href = link['href']
                                    if '.pdf' in href.lower():
                                        download_links['pdf'] = f"{self.base_url}{href}" if not href.startswith('http') else href
                                    elif '.docx' in href.lower() or '.doc' in href.lower():
                                        download_links['docx'] = f"{self.base_url}{href}" if not href.startswith('http') else href
                                
                                forms.append({
                                    'form_number': form_number,
                                    'form_title': self.clean_form_title(text),
                                    'form_url': self.forms_url,
                                    'form_type': self.determine_form_type(text),
                                    'category': self.determine_category(text, form_number),
                                    'download_links': download_links,
                                    'description': '',
                                    'has_children_section': self.check_children_section(text, form_number),
                                    'requires_financial': self.check_financial_requirement(form_number),
                                    'has_property_section': self.check_property_section(form_number)
                                })
                                break
        
        return forms
    
    def get_form_details(self, form_url: str) -> Dict:
        """Get additional details from the form's detail page"""
        details = {'download_links': {}, 'description': ''}
        
        try:
            response = self.session.get(form_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find download links
                links = soup.find_all('a', href=re.compile(r'\.(pdf|docx?|odt)$', re.I))
                for link in links:
                    href = link['href']
                    if not href.startswith('http'):
                        href = f"{self.base_url}{href}"
                    
                    if '.pdf' in href.lower():
                        details['download_links']['pdf'] = href
                    elif '.docx' in href.lower() or '.doc' in href.lower():
                        details['download_links']['docx'] = href
                
                # Extract description if available
                desc_elem = soup.find(['p', 'div'], class_=re.compile(r'description|summary'))
                if desc_elem:
                    details['description'] = desc_elem.get_text(strip=True)[:500]
                    
        except Exception as e:
            logger.debug(f"Could not get details for {form_url}: {e}")
            
        return details
    
    def extract_form_number(self, url: str, text: str) -> str:
        """Extract form number from URL or text"""
        # Try URL first
        url_match = re.search(r'/(\d+[a-z]?(?:\.\d+)?)[/_]', url.lower())
        if url_match:
            return url_match.group(1).upper()
            
        # Try text
        text_patterns = [
            r'Form\s+(\d+[A-Z]?(?:\.\d+)?)',
            r'FLR-(\d+[A-Z]?(?:\.\d+)?)',
            r'(\d+[A-Z]?(?:\.\d+)?)\s*[-–]\s*\w+',
        ]
        
        for pattern in text_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                form_num = match.group(1).upper()
                # Clean up form number
                form_num = form_num.replace('FLR-', '').replace('FLR', '')
                return form_num
                
        return None
    
    def clean_form_title(self, text: str) -> str:
        """Clean and standardize form title"""
        # Remove form number from title
        title = re.sub(r'^Form\s+\d+[A-Z]?(?:\.\d+)?\s*[-–:]?\s*', '', text, flags=re.I)
        title = re.sub(r'^\d+[A-Z]?(?:\.\d+)?\s*[-–:]?\s*', '', title)
        title = re.sub(r'^FLR-\d+[A-Z]?(?:\.\d+)?\s*[-–:]?\s*', '', title, flags=re.I)
        
        # Clean up
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        
        # Remove file extensions
        title = re.sub(r'\.(pdf|docx?|odt)$', '', title, flags=re.I)
        
        return title
    
    def determine_form_type(self, title: str) -> str:
        """Determine form type based on title"""
        title_lower = title.lower()
        
        if 'application' in title_lower:
            return 'application'
        elif 'answer' in title_lower or 'reply' in title_lower:
            return 'answer'
        elif 'motion' in title_lower:
            return 'motion'
        elif 'affidavit' in title_lower:
            return 'affidavit'
        elif 'financial' in title_lower:
            return 'financial'
        elif 'order' in title_lower:
            return 'order'
        elif 'notice' in title_lower:
            return 'notice'
        elif 'certificate' in title_lower:
            return 'certificate'
        elif 'consent' in title_lower:
            return 'consent'
        elif 'brief' in title_lower or 'conference' in title_lower:
            return 'conference'
        else:
            return 'general'
    
    def determine_category(self, title: str, form_number: str) -> str:
        """Determine category based on title and form number"""
        title_lower = title.lower()
        form_num = form_number.replace('.', '')
        
        # Check by form number ranges
        if form_num.startswith('8'):
            return 'applications'
        elif form_num.startswith('10'):
            return 'answers'
        elif form_num in ['13', '131', '13A', '13B', '13C']:
            return 'financial'
        elif form_num.startswith('14') or form_num.startswith('15'):
            return 'motions'
        elif form_num.startswith('17'):
            return 'conferences'
        elif form_num.startswith('25'):
            return 'orders'
        elif form_num.startswith('36'):
            return 'divorce'
        elif form_num.startswith('34') or form_num.startswith('33'):
            return 'children'
        
        # Check by keywords
        if 'divorce' in title_lower:
            return 'divorce'
        elif 'child' in title_lower or 'custody' in title_lower or 'access' in title_lower:
            return 'children'
        elif 'support' in title_lower:
            return 'support'
        elif 'property' in title_lower:
            return 'property'
        elif 'enforcement' in title_lower or 'garnish' in title_lower:
            return 'enforcement'
        elif 'service' in title_lower:
            return 'service'
        
        return 'general'
    
    def check_children_section(self, title: str, form_number: str) -> bool:
        """Check if form has children section"""
        keywords = ['child', 'custody', 'access', 'parenting', 'support']
        return any(kw in title.lower() for kw in keywords) or form_number in ['8', '8A', '10', '33F', '34']
    
    def check_financial_requirement(self, form_number: str) -> bool:
        """Check if form requires financial information"""
        financial_forms = ['8', '8A', '10', '13', '13.1', '13A', '13B', '13C', '15', '26', '27']
        return any(form_number.startswith(f) for f in financial_forms)
    
    def check_property_section(self, form_number: str) -> bool:
        """Check if form has property section"""
        property_forms = ['8', '8A', '10', '13.1', '13B', '13C']
        return any(form_number.startswith(f) for f in property_forms)
    
    def save_to_json(self, forms: List[Dict], output_file: str = "ontario_forms_registry.json"):
        """Save scraped forms to JSON file"""
        output_path = Path(output_file)
        
        # Sort forms by form number
        forms.sort(key=lambda x: (
            int(re.search(r'\d+', x['form_number']).group()),
            x['form_number']
        ))
        
        with open(output_path, 'w') as f:
            json.dump({
                'source': self.forms_url,
                'total_forms': len(forms),
                'forms': forms
            }, f, indent=2)
            
        logger.info(f"Saved {len(forms)} forms to {output_path}")
        return output_path
    
    def generate_form_registry_code(self, forms: List[Dict]) -> str:
        """Generate Python code for FormRegistry"""
        code = '''# Auto-generated FormRegistry from Ontario Court Forms website
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class FormConfiguration:
    form_number: str
    form_title: str
    form_type: str
    category: str
    url: str
    filename: str
    requires_financial: bool = False
    has_children_section: bool = False
    has_property_section: bool = False
    dependencies: List[str] = field(default_factory=list)
    download_links: Dict[str, str] = field(default_factory=dict)

class FormRegistry:
    """Registry of all Ontario family law forms"""
    
    FORMS = [
'''
        
        for form in forms:
            # Generate filename
            form_num_clean = form['form_number'].replace('.', '_').lower()
            filename = f"form_{form_num_clean}.pdf"
            
            code += f'''        FormConfiguration(
            form_number="{form['form_number']}",
            form_title="{form['form_title']}",
            form_type="{form['form_type']}",
            category="{form['category']}",
            url="{form['form_url']}",
            filename="{filename}",
            requires_financial={form['requires_financial']},
            has_children_section={form['has_children_section']},
            has_property_section={form['has_property_section']},
            download_links={form['download_links']}
        ),
'''
        
        code += '''    ]
    
    @classmethod
    def get_all_forms(cls):
        return cls.FORMS
    
    @classmethod
    def get_form_by_number(cls, form_number: str):
        for form in cls.FORMS:
            if form.form_number == form_number:
                return form
        return None
'''
        
        return code

def main():
    """Main function to scrape and save forms"""
    scraper = OntarioFormsScraper()
    
    # Scrape all forms
    forms = scraper.scrape_all_forms()
    
    # Save to JSON
    json_path = scraper.save_to_json(forms)
    
    # Generate FormRegistry code
    registry_code = scraper.generate_form_registry_code(forms)
    
    # Save FormRegistry code
    with open('form_registry_generated.py', 'w') as f:
        f.write(registry_code)
    
    logger.info(f"Successfully scraped {len(forms)} forms")
    logger.info(f"JSON saved to: {json_path}")
    logger.info("FormRegistry code saved to: form_registry_generated.py")
    
    return forms

if __name__ == "__main__":
    main()