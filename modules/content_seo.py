"""
Content SEO Analysis Module
Handles analysis of content elements like paragraphs, images, and alt text.
"""

def analyze(response, soup):
    """Analyze content SEO elements."""
    paragraphs = soup.find_all('p')
    images = soup.find_all('img')
    
    return {
        'Word Count': len(response.text.split()),
        'Paragraph Count': len(paragraphs),
        'Image Count': len(images),
        'Images with Alt Text': len([img for img in images if img.get('alt')])
    } 