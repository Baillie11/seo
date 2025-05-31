"""
Speed Insights Module
Provides detailed performance analysis and optimization recommendations.
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import re
from concurrent.futures import ThreadPoolExecutor

def analyze_resource_size(url, resource_url):
    """Analyze the size of a single resource."""
    try:
        response = requests.head(urljoin(url, resource_url), timeout=10)
        size = int(response.headers.get('content-length', 0))
        return {
            'url': resource_url,
            'size': size,
            'size_kb': round(size / 1024, 2) if size else 0
        }
    except Exception:
        return {
            'url': resource_url,
            'size': 0,
            'size_kb': 0,
            'error': 'Failed to fetch resource'
        }

def check_resource_optimization(soup, base_url):
    """Check resource optimization opportunities."""
    resources = {
        'js': [],
        'css': [],
        'images': [],
        'fonts': []
    }
    
    # Collect JavaScript files
    for script in soup.find_all('script', src=True):
        resources['js'].append(script['src'])
    
    # Collect CSS files
    for css in soup.find_all('link', rel='stylesheet'):
        resources['css'].append(css.get('href', ''))
    
    # Collect images
    for img in soup.find_all('img'):
        resources['images'].append(img.get('src', ''))
    
    # Collect fonts
    for font in soup.find_all('link', rel='preload', as_='font'):
        resources['fonts'].append(font.get('href', ''))
    
    # Analyze resource sizes in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = {}
        for resource_type, urls in resources.items():
            results[resource_type] = list(executor.map(
                lambda url: analyze_resource_size(base_url, url),
                urls
            ))
    
    return results

def analyze_render_blocking_resources(soup):
    """Analyze render-blocking resources."""
    blocking_resources = []
    
    # Check for render-blocking CSS
    for css in soup.find_all('link', rel='stylesheet'):
        if not css.get('media') or css['media'] == 'all':
            blocking_resources.append({
                'type': 'css',
                'url': css['href'],
                'recommendation': 'Consider adding media queries or loading asynchronously'
            })
    
    # Check for render-blocking JavaScript
    for script in soup.find_all('script', src=True):
        if not script.get('async') and not script.get('defer'):
            blocking_resources.append({
                'type': 'javascript',
                'url': script['src'],
                'recommendation': 'Add async or defer attribute'
            })
    
    return blocking_resources

def check_caching_headers(url, resources):
    """Check caching headers for resources."""
    caching_issues = []
    
    for resource_type, resource_list in resources.items():
        for resource in resource_list:
            try:
                response = requests.head(urljoin(url, resource['url']), timeout=10)
                cache_control = response.headers.get('cache-control', '')
                
                if not cache_control:
                    caching_issues.append({
                        'type': resource_type,
                        'url': resource['url'],
                        'issue': 'No cache-control header',
                        'recommendation': 'Add cache-control headers'
                    })
                elif 'no-cache' in cache_control or 'no-store' in cache_control:
                    caching_issues.append({
                        'type': resource_type,
                        'url': resource['url'],
                        'issue': 'Caching disabled',
                        'recommendation': 'Enable caching for static resources'
                    })
            except Exception:
                continue
    
    return caching_issues

def analyze_speed(url):
    """Analyze website speed and performance."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=20)
        load_time = time.time() - start_time
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Analyze resources
        resource_analysis = check_resource_optimization(soup, url)
        
        # Get render-blocking resources
        blocking_resources = analyze_render_blocking_resources(soup)
        
        # Check caching
        caching_issues = check_caching_headers(url, resource_analysis)
        
        # Calculate total resource sizes
        total_sizes = {
            resource_type: sum(r['size_kb'] for r in resources)
            for resource_type, resources in resource_analysis.items()
        }
        
        # Generate recommendations
        recommendations = []
        
        # Check total page size
        total_page_size = sum(total_sizes.values())
        if total_page_size > 5000:  # 5MB threshold
            recommendations.append({
                'priority': 'high',
                'message': f'Total page size ({round(total_page_size/1024, 2)}MB) is too large',
                'recommendation': 'Optimize and compress resources'
            })
        
        # Check load time
        if load_time > 3:  # 3 seconds threshold
            recommendations.append({
                'priority': 'high',
                'message': f'Page load time ({round(load_time, 2)}s) is too high',
                'recommendation': 'Optimize performance and reduce server response time'
            })
        
        # Add recommendations for blocking resources
        if blocking_resources:
            recommendations.append({
                'priority': 'medium',
                'message': f'Found {len(blocking_resources)} render-blocking resources',
                'recommendation': 'Optimize resource loading with async/defer'
            })
        
        # Add recommendations for caching
        if caching_issues:
            recommendations.append({
                'priority': 'medium',
                'message': f'Found {len(caching_issues)} resources with caching issues',
                'recommendation': 'Implement proper caching headers'
            })
        
        return {
            'status': 'success',
            'load_time': round(load_time, 2),
            'page_size': {
                'total': round(total_page_size, 2),
                'breakdown': {k: round(v, 2) for k, v in total_sizes.items()}
            },
            'resources': resource_analysis,
            'blocking_resources': blocking_resources,
            'caching_issues': caching_issues,
            'recommendations': recommendations,
            'performance_score': max(0, 100 - (
                (load_time > 3) * 20 +  # Penalty for slow load time
                (total_page_size > 5000) * 20 +  # Penalty for large page size
                len(blocking_resources) * 5 +  # Penalty for blocking resources
                len(caching_issues) * 5  # Penalty for caching issues
            ))
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 