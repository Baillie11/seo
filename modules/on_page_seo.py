"""
On-Page SEO Analysis Module
Handles analysis of title tags, meta descriptions, and heading structure.
"""

def analyze(response, soup):
    """Analyze on-page SEO elements."""
    title_tag = soup.find('title')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    h1_tags = soup.find_all('h1')
    
    return {
        'Title': title_tag.text if title_tag else "No title tag found",
        'Title Length': len(title_tag.text) if title_tag else 0,
        'Meta Description': meta_description['content'] if meta_description else "No meta description found",
        'Meta Description Length': len(meta_description['content']) if meta_description else 0,
        'H1 Count': len(h1_tags),
        'H1 Tags': [tag.text for tag in h1_tags[:3]]  # First 3 H1 tags
    } 