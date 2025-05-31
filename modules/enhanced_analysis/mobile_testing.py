"""
Mobile Testing Module
Analyzes mobile-friendliness and responsiveness of websites.
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def check_viewport(soup):
    """Check if viewport meta tag is properly set."""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport:
        return {
            'status': 'error',
            'message': 'No viewport meta tag found',
            'recommendation': 'Add viewport meta tag for proper mobile rendering'
        }
    
    content = viewport.get('content', '')
    if 'width=device-width' not in content or 'initial-scale=1' not in content:
        return {
            'status': 'warning',
            'message': 'Viewport meta tag may not be properly configured',
            'recommendation': 'Set viewport with width=device-width and initial-scale=1'
        }
    
    return {
        'status': 'success',
        'message': 'Viewport meta tag properly configured'
    }

def check_font_sizes(soup):
    """Check for mobile-friendly font sizes."""
    issues = []
    
    # Check font-size in style attributes
    elements_with_style = soup.find_all(style=True)
    for element in elements_with_style:
        style = element.get('style', '')
        if 'font-size' in style:
            size = re.search(r'font-size:\s*(\d+)px', style)
            if size and int(size.group(1)) < 12:
                issues.append({
                    'element': element.name,
                    'current_size': f"{size.group(1)}px",
                    'recommendation': 'Increase font size to at least 12px for mobile readability'
                })
    
    return {
        'status': 'warning' if issues else 'success',
        'issues': issues
    }

def check_tap_targets(soup):
    """Check for properly sized tap targets."""
    issues = []
    
    # Check links and buttons
    clickable_elements = soup.find_all(['a', 'button'])
    for element in clickable_elements:
        style = element.get('style', '')
        
        # Check for small heights/widths in style attribute
        if any(dim in style for dim in ['height', 'width']):
            dimensions = re.findall(r'(height|width):\s*(\d+)px', style)
            for dim_type, size in dimensions:
                if int(size) < 44:  # Minimum recommended tap target size
                    issues.append({
                        'element': element.name,
                        'dimension': dim_type,
                        'current_size': f"{size}px",
                        'recommendation': f'Increase {dim_type} to at least 44px for better tap targets'
                    })
    
    return {
        'status': 'warning' if issues else 'success',
        'issues': issues
    }

def check_responsive_images(soup, base_url):
    """Check for responsive images."""
    issues = []
    
    images = soup.find_all('img')
    for img in images:
        # Check for srcset attribute
        if not img.get('srcset'):
            issues.append({
                'element': 'img',
                'src': urljoin(base_url, img.get('src', '')),
                'recommendation': 'Add srcset attribute for responsive images'
            })
        
        # Check for width and height attributes
        if not (img.get('width') and img.get('height')):
            issues.append({
                'element': 'img',
                'src': urljoin(base_url, img.get('src', '')),
                'recommendation': 'Add width and height attributes to prevent layout shifts'
            })
    
    return {
        'status': 'warning' if issues else 'success',
        'issues': issues
    }

def analyze_mobile_friendliness(url):
    """Analyze mobile-friendliness of a website."""
    try:
        # Use a mobile user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {
            'viewport': check_viewport(soup),
            'font_sizes': check_font_sizes(soup),
            'tap_targets': check_tap_targets(soup),
            'responsive_images': check_responsive_images(soup, url)
        }
        
        # Calculate overall score
        issues_count = sum(1 for check in results.values() 
                         if check['status'] in ['error', 'warning'])
        
        mobile_score = max(0, 100 - (issues_count * 10))
        
        return {
            'status': 'success',
            'mobile_score': mobile_score,
            'checks': results,
            'summary': {
                'critical_issues': len([c for c in results.values() if c['status'] == 'error']),
                'warnings': len([c for c in results.values() if c['status'] == 'warning']),
                'passed_checks': len([c for c in results.values() if c['status'] == 'success'])
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 