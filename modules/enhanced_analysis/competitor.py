"""
Competitor Analysis Module
Compares multiple websites and provides competitive insights.
"""

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from ..technical_seo import analyze as technical_analysis
from ..content_seo import analyze as content_analysis
from ..on_page_seo import analyze as onpage_analysis

def analyze_competitor(url):
    """Analyze a single competitor website."""
    try:
        response = requests.get(url, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'url': url,
            'technical': technical_analysis(response, soup),
            'content': content_analysis(response, soup),
            'onpage': onpage_analysis(response, soup),
            'status': 'success'
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'message': str(e)
        }

def compare_websites(main_url, competitor_urls):
    """Compare main website with competitor websites."""
    # Analyze all websites in parallel
    urls = [main_url] + competitor_urls
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(analyze_competitor, urls))
    
    main_site = results[0]
    competitor_sites = results[1:]
    
    comparison = {
        'main_site': main_site,
        'competitors': competitor_sites,
        'summary': {}
    }
    
    if main_site['status'] == 'success':
        # Calculate averages and comparisons
        comparison['summary'] = {
            'word_count': {
                'main': main_site['content'].get('Word Count', 0),
                'avg_competitors': sum(c['content'].get('Word Count', 0) 
                                    for c in competitor_sites 
                                    if c['status'] == 'success') / len(competitor_sites)
            },
            'load_time': {
                'main': main_site['technical'].get('Page Load Time', '0'),
                'avg_competitors': sum(float(c['technical'].get('Page Load Time', '0').split()[0]) 
                                    for c in competitor_sites 
                                    if c['status'] == 'success') / len(competitor_sites)
            },
            'meta_tags': {
                'main': bool(main_site['onpage'].get('Meta Description', False)),
                'competitors_with_meta': sum(1 for c in competitor_sites 
                                          if c['status'] == 'success' and 
                                          c['onpage'].get('Meta Description', False))
            }
        }
    
    return comparison 