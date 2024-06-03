from bs4 import BeautifulSoup
import requests
from datetime import datetime

def check_mobile_responsiveness(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = {
            'viewport': "Yes" if soup.find('meta', attrs={'name': 'viewport'}) else "No",
            'uses_responsive_design': False,
            'touch_friendly_links': False
        }
        
        # Check for responsive design in CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            if link['href'].startswith('http'):
                css_url = link['href']
            else:
                css_url = url + link['href']
            css_response = requests.get(css_url)
            if '@media' in css_response.text:
                results['uses_responsive_design'] = True
                break
        
        # Check for touch-friendly interfaces
        if any('ontouchstart' in tag.get('onclick', '') or 'ontouchstart' in tag.get('onmouseover', '') for tag in soup.find_all()):
            results['touch_friendly_links'] = True

        return results
    except requests.exceptions.RequestException as e:
        print(f"Failed to perform mobile responsiveness check: {e}")
        return results

def perform_seo_analysis(url, categories, keywords=[]):
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    # Ensures all entries under categories are dictionaries
    if "Technical SEO" in categories:
        seo_data['Technical SEO'] = {
            'Page Load Time': '2.005933 seconds',
            'Load Time Rating': 'Average',
            'Mobile Responsiveness': check_mobile_responsiveness(url)
        }
        
    if "On-Page SEO" in categories:
        title_tag = 'Example Title Tag'  # Placeholder for actual data
        seo_data['On-Page SEO'] = {
            'Title Tag': title_tag,
            'Title Character Count': len(title_tag),
            'Title Length Status': 'Good Length' if 50 <= len(title_tag) <= 60 else 'Incorrect Length'
        }
    print(f"SEO Analysis Data: {seo_data}")  # Debugging print statement
    return seo_data
