"""
Schema Markup Analysis Module
Handles analysis of structured data and social media tags.
"""

def analyze(response, soup):
    """Analyze schema markup and social media elements."""
    schema_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    social_meta = {
        'og:title': soup.find('meta', {'property': 'og:title'}),
        'og:description': soup.find('meta', {'property': 'og:description'}),
        'og:image': soup.find('meta', {'property': 'og:image'}),
        'twitter:card': soup.find('meta', {'name': 'twitter:card'}),
        'twitter:title': soup.find('meta', {'name': 'twitter:title'})
    }
    
    return {
        'JSON-LD Scripts': len(schema_scripts),
        'Schema Types': [script.string.split('"@type":')[1].split('"')[1] 
                        for script in schema_scripts 
                        if script.string and '"@type":' in script.string],
        'OpenGraph Tags': {k: v['content'] if v else 'Not found' 
                          for k, v in social_meta.items() 
                          if k.startswith('og:')},
        'Twitter Cards': {k: v['content'] if v else 'Not found' 
                         for k, v in social_meta.items() 
                         if k.startswith('twitter:')}
    } 