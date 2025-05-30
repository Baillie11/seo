"""
Security Analysis Module
Handles analysis of security headers and HTTPS implementation.
"""

def analyze(response, url):
    """Analyze security elements."""
    security_headers = {
        'Strict-Transport-Security': response.headers.get('Strict-Transport-Security', 'Not set'),
        'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', 'Not set'),
        'X-Frame-Options': response.headers.get('X-Frame-Options', 'Not set'),
        'Content-Security-Policy': response.headers.get('Content-Security-Policy', 'Not set')
    }
    
    return {
        'HTTPS': url.startswith('https://'),
        'Security Headers': security_headers
    } 