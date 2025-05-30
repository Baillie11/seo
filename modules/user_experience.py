"""
User Experience Analysis Module
Handles analysis of mobile responsiveness and link structure.
"""

def analyze(response, soup, url):
    """Analyze user experience elements."""
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    links = soup.find_all('a')
    
    return {
        'Mobile Responsive': "Yes" if viewport_meta else "No",
        'Total Links': len(links),
        'Internal Links': len([link for link in links if link.get('href', '').startswith(('/', url))]),
        'External Links': len([link for link in links if link.get('href', '').startswith('http')])
    } 