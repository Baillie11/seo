"""
Technical SEO Analysis Module
Handles all technical SEO checks including load time, status codes, and response sizes.
"""

import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

def check_robots_txt(url):
    """Check for robots.txt file and its configuration."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    base_domain = parsed_url.netloc
    
    try:
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            # Check for complete site blocking
            if 'disallow: /' in content and not any(line.strip().startswith('allow: /') for line in content.splitlines()):
                return {
                    "status": "warning",
                    "message": "Present but blocking all content",
                    "content": response.text,
                    "needs_creation": False
                }
            # Check for sitemap reference
            if 'sitemap:' not in content:
                return {
                    "status": "warning",
                    "message": "Present but missing sitemap reference",
                    "content": response.text,
                    "needs_creation": False
                }
            return {
                "status": "success",
                "message": "Present and properly configured",
                "content": response.text,
                "needs_creation": False
            }
        return {
            "status": "error",
            "message": "Missing",
            "suggested_content": f"""User-agent: *
Allow: /

# Allow crawling of all content
Sitemap: {parsed_url.scheme}://{base_domain}/sitemap.xml

# Common directories to consider disallowing
# Disallow: /admin/
# Disallow: /private/
# Disallow: /tmp/
# Disallow: /includes/""",
            "needs_creation": True
        }
    except:
        return {
            "status": "error",
            "message": "Not accessible",
            "needs_creation": True,
            "suggested_content": f"""User-agent: *
Allow: /

# Allow crawling of all content
Sitemap: {parsed_url.scheme}://{base_domain}/sitemap.xml

# Common directories to consider disallowing
# Disallow: /admin/
# Disallow: /private/
# Disallow: /tmp/
# Disallow: /includes/"""
        }

def check_sitemap(url, soup):
    """Check for sitemap.xml file and its configuration."""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # List of common sitemap locations to check
    sitemap_locations = [
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/sitemap/sitemap.xml"
    ]
    
    # Also check robots.txt for Sitemap directive
    robots_url = f"{base_url}/robots.txt"
    try:
        robots_response = requests.get(robots_url, timeout=10)
        if robots_response.status_code == 200:
            for line in robots_response.text.splitlines():
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_locations.insert(0, sitemap_url)
    except:
        pass

    # Get all URLs from the current page
    page_urls = [a.get('href') for a in soup.find_all('a', href=True)]
    page_urls = [url for url in page_urls if url.startswith('/') or url.startswith(base_url)]
    
    # Convert relative URLs to absolute
    page_urls = [url if url.startswith('http') else f"{base_url}{url}" for url in page_urls]
    
    # Remove duplicates and fragments
    page_urls = list(set([url.split('#')[0] for url in page_urls]))
    
    # Check each potential sitemap location
    for sitemap_url in sitemap_locations:
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                try:
                    # Try to parse as XML to validate structure
                    ET.fromstring(response.content)
                    return {
                        "status": "success",
                        "message": "Present and valid XML",
                        "content": response.text,
                        "needs_creation": False,
                        "url": sitemap_url
                    }
                except ET.ParseError:
                    return {
                        "status": "warning",
                        "message": "Present but invalid XML format",
                        "content": response.text,
                        "needs_creation": True,
                        "suggested_content": generate_sitemap_content(base_url, page_urls)
                    }
        except:
            continue
    
    # If no sitemap found, suggest creation
    return {
        "status": "error",
        "message": "Missing",
        "needs_creation": True,
        "suggested_content": generate_sitemap_content(base_url, page_urls)
    }

def generate_sitemap_content(base_url, urls):
    """Generate sitemap.xml content based on discovered URLs."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    
    # Add base URL
    sitemap_content += f"""    <url>
        <loc>{base_url}</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
"""
    
    # Add discovered URLs
    for url in urls:
        sitemap_content += f"""    <url>
        <loc>{url}</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    
    sitemap_content += "</urlset>"
    return sitemap_content

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
    
    robots_check = check_robots_txt(url)
    sitemap_check = check_sitemap(url, soup)
    
    results = {
        'Load Time': f"{load_time:.2f} seconds",
        'Mobile Friendly': check_mobile_friendly(response),
        'SSL Certificate': 'Valid SSL certificate' if url.startswith('https://') else 'No SSL or expired',
        'Robots.txt': {
            'status': robots_check['status'],
            'message': robots_check['message'],
            'needs_creation': robots_check.get('needs_creation', False)
        },
        'Sitemap.xml': {
            'status': sitemap_check['status'],
            'message': sitemap_check['message'],
            'needs_creation': sitemap_check.get('needs_creation', False)
        }
    }
    
    if robots_check.get('suggested_content'):
        results['Robots.txt']['suggested_content'] = robots_check['suggested_content']
    elif robots_check.get('content'):
        results['Robots.txt']['content'] = robots_check['content']
        
    if sitemap_check.get('suggested_content'):
        results['Sitemap.xml']['suggested_content'] = sitemap_check['suggested_content']
    elif sitemap_check.get('content'):
        results['Sitemap.xml']['content'] = sitemap_check['content']
    
    # Add load time rating based on modern performance standards
    if load_time < 1:
        results['Load Time Rating'] = "Excellent"
    elif load_time < 2:
        results['Load Time Rating'] = "Good"
    elif load_time < 3:
        results['Load Time Rating'] = "Warning"
    elif load_time < 5:
        results['Load Time Rating'] = "Poor"
    else:
        results['Load Time Rating'] = "Critical"
        
    return results 