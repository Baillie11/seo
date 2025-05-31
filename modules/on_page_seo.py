"""
On-Page SEO Analysis Module
Handles analysis of title tags, meta descriptions, and heading structure.
"""

def analyze_title(title_tag):
    """Analyze the title tag."""
    if not title_tag:
        return {
            'value': "Missing",
            'status': "bad"
        }
    
    title_text = title_tag.text
    title_len = len(title_text)
    
    if 50 <= title_len <= 60:
        status = "good"
    elif 40 <= title_len < 50 or 60 < title_len <= 70:
        status = "warning"
    else:
        status = "bad"
        
    return {
        'value': title_text,
        'length': title_len,
        'status': status
    }

def analyze_meta_description(meta_description):
    """Analyze the meta description."""
    if not meta_description:
        return {
            'value': "Missing",
            'status': "bad"
        }
    
    desc_text = meta_description['content']
    desc_len = len(desc_text)
    
    if 150 <= desc_len <= 160:
        status = "good"
    elif 130 <= desc_len < 150 or 160 < desc_len <= 180:
        status = "warning"
    else:
        status = "bad"
        
    return {
        'value': desc_text,
        'length': desc_len,
        'status': status
    }

def analyze_headers(soup):
    """Analyze header tag structure."""
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    h3_tags = soup.find_all('h3')
    
    # Check header hierarchy
    if len(h1_tags) == 1 and len(h2_tags) > 0:
        status = "good"
    elif len(h1_tags) == 1 and len(h2_tags) == 0:
        status = "warning"
    else:
        status = "bad"
    
    return {
        'h1_count': len(h1_tags),
        'h2_count': len(h2_tags),
        'h3_count': len(h3_tags),
        'h1_text': [tag.text for tag in h1_tags[:3]],  # First 3 H1 tags
        'status': status
    }

def analyze(response, soup):
    """Analyze on-page SEO elements."""
    title_tag = soup.find('title')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    
    title_analysis = analyze_title(title_tag)
    meta_analysis = analyze_meta_description(meta_description)
    header_analysis = analyze_headers(soup)
    
    return {
        'Title Tag': {
            'Content': title_analysis['value'],
            'Length': title_analysis['length'] if 'length' in title_analysis else 0,
            'Status': title_analysis['status']
        },
        'Meta Description': {
            'Content': meta_analysis['value'],
            'Length': meta_analysis['length'] if 'length' in meta_analysis else 0,
            'Status': meta_analysis['status']
        },
        'Header Tags': {
            'H1 Count': header_analysis['h1_count'],
            'H2 Count': header_analysis['h2_count'],
            'H3 Count': header_analysis['h3_count'],
            'H1 Content': header_analysis['h1_text'],
            'Structure Status': header_analysis['status']
        }
    } 