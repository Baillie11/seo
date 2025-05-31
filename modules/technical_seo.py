"""
Technical SEO Analysis Module
Handles all technical SEO checks including load time, status codes, and response sizes.
"""

import os
import requests
from urllib.parse import urlparse

def check_robots_txt(url):
    """Check for robots.txt file and its configuration."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    try:
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            if 'disallow: /' in content:
                return "Present but blocking important content"
            elif len(content.strip()) < 10:
                return "Present but needs optimization"
            return "Present and properly configured"
        return "Missing"
    except:
        return "Not accessible"

def check_mobile_friendly(response):
    """Check if the site appears to be mobile friendly."""
    viewport_meta = response.text.lower().find('name="viewport"')
    responsive_meta = response.text.lower().find('media="screen and (')
    if viewport_meta > -1 or responsive_meta > -1:
        return "Yes"
    return "No"

def analyze(response, soup):
    """Analyze technical SEO aspects of the webpage."""
    load_time = response.elapsed.total_seconds()
    url = str(response.url)
    
    results = {
        'Load Time': f"{load_time:.2f} seconds",
        'Mobile Friendly': check_mobile_friendly(response),
        'SSL Certificate': 'Valid SSL certificate' if url.startswith('https://') else 'No SSL or expired',
        'Robots.txt': check_robots_txt(url)
    }
    
    # Add load time rating based on metrics guide thresholds
    if load_time < 3:
        results['Load Time Rating'] = "Good"
    elif load_time < 5:
        results['Load Time Rating'] = "Warning"
    else:
        results['Load Time Rating'] = "Poor"
        
    return results 