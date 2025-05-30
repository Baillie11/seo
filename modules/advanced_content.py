"""
Advanced Content Analysis Module
Handles in-depth content analysis including keyword density and broken links.
"""

import requests

def analyze(response, soup):
    """Analyze advanced content elements."""
    all_text = soup.get_text()
    words = all_text.lower().split()
    word_count = len(words)
    
    # Keyword density analysis
    common_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 
                       'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'])
    word_freq = {}
    for word in words:
        if word not in common_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Heading hierarchy analysis
    headings = {
        'h1': len(soup.find_all('h1')),
        'h2': len(soup.find_all('h2')),
        'h3': len(soup.find_all('h3')),
        'h4': len(soup.find_all('h4')),
        'h5': len(soup.find_all('h5')),
        'h6': len(soup.find_all('h6'))
    }
    
    # Broken link analysis
    links = soup.find_all('a')
    broken_links = []
    for link in links[:10]:  # Check first 10 links
        href = link.get('href')
        if href and href.startswith(('http://', 'https://')):
            try:
                head_response = requests.head(href, timeout=5)
                if head_response.status_code >= 400:
                    broken_links.append(href)
            except:
                broken_links.append(href)
    
    # Content-to-HTML ratio
    html_size = len(response.text)
    text_size = len(all_text)
    content_ratio = (text_size / html_size) * 100 if html_size > 0 else 0
    
    return {
        'Word Count': word_count,
        'Top Keywords': sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5],
        'Heading Structure': headings,
        'Content-to-HTML Ratio': f"{content_ratio:.2f}%",
        'Broken Links Found': len(broken_links),
        'Broken Links': broken_links[:5] if broken_links else "None found"
    } 