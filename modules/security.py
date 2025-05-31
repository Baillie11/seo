"""
Security Analysis Module
Handles analysis of HTTPS and mixed content.
"""

from bs4 import BeautifulSoup

def analyze_https(url):
    """Analyze HTTPS configuration."""
    if url.startswith('https://'):
        return {
            'status': "good",
            'message': "HTTPS enabled and properly configured"
        }
    return {
        'status': "bad",
        'message': "No HTTPS or misconfigured"
    }

def analyze_mixed_content(response, soup):
    """Analyze for mixed content issues."""
    if not response.url.startswith('https://'):
        return {
            'status': "bad",
            'message': "Site not using HTTPS, mixed content check not applicable"
        }
    
    # Check for mixed content in various elements
    mixed_active = []
    mixed_passive = []
    
    # Check scripts
    for script in soup.find_all('script', src=True):
        src = script['src']
        if src.startswith('http://'):
            mixed_active.append(('script', src))
    
    # Check stylesheets
    for link in soup.find_all('link', rel='stylesheet', href=True):
        href = link['href']
        if href.startswith('http://'):
            mixed_active.append(('stylesheet', href))
    
    # Check images
    for img in soup.find_all('img', src=True):
        src = img['src']
        if src.startswith('http://'):
            mixed_passive.append(('image', src))
    
    # Check media elements
    for media in soup.find_all(['audio', 'video'], src=True):
        src = media['src']
        if src.startswith('http://'):
            mixed_passive.append(('media', src))
    
    if mixed_active:
        return {
            'status': "bad",
            'message': f"Found {len(mixed_active)} active mixed content issues",
            'details': mixed_active
        }
    elif mixed_passive:
        return {
            'status': "warning",
            'message': f"Found {len(mixed_passive)} passive mixed content issues",
            'details': mixed_passive
        }
    return {
        'status': "good",
        'message': "No mixed content found"
    }

def analyze(response, url):
    """Analyze security aspects."""
    https_analysis = analyze_https(url)
    mixed_content_analysis = analyze_mixed_content(response, BeautifulSoup(response.text, 'html.parser'))
    
    return {
        'HTTPS': {
            'Status': https_analysis['status'],
            'Details': https_analysis['message']
        },
        'Mixed Content': {
            'Status': mixed_content_analysis['status'],
            'Details': mixed_content_analysis['message']
        }
    } 