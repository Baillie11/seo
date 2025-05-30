"""
Technical SEO Analysis Module
Handles all technical SEO checks including load time, status codes, and response sizes.
"""

def analyze(response, soup):
    """Analyze technical SEO aspects of the webpage."""
    load_time = response.elapsed.total_seconds()
    
    results = {
        'Page Load Time': f"{load_time} seconds",
        'Status Code': response.status_code,
        'Response Size': f"{len(response.content) / 1024:.2f} KB"
    }
    
    # Load time rating
    if load_time < 2:
        results['Load Time Rating'] = "Good"
    elif load_time < 5:
        results['Load Time Rating'] = "Average"
    else:
        results['Load Time Rating'] = "Poor"
        
    return results 