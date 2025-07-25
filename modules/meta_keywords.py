"""
Meta Keywords Analysis Module
Analyzes webpage content and generates relevant meta keywords.
"""

import re
from collections import Counter
from urllib.parse import urlparse
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_text_content(soup):
    """Extract and clean text content from the webpage."""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text from important SEO elements
    title_text = ""
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
    
    meta_desc_text = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        meta_desc_text = meta_desc.get('content', '')
    
    # Get text from headers (h1-h6)
    headers_text = ""
    for i in range(1, 7):
        headers = soup.find_all(f'h{i}')
        headers_text += " ".join([h.get_text() for h in headers]) + " "
    
    # Get main body text
    body_text = soup.get_text()
    
    # Clean and combine all text
    all_text = f"{title_text} {meta_desc_text} {headers_text} {body_text}"
    
    # Clean the text
    all_text = re.sub(r'\s+', ' ', all_text)  # Replace multiple spaces with single space
    all_text = re.sub(r'[^\w\s]', ' ', all_text)  # Remove special characters
    
    return all_text.lower().strip()

def get_existing_meta_keywords(soup):
    """Check if meta keywords already exist."""
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        keywords = meta_keywords.get('content', '').strip()
        if keywords:
            return [kw.strip() for kw in keywords.split(',')]
    return []

def extract_keywords_from_text(text, max_keywords=15):
    """Extract relevant keywords from text content."""
    try:
        # Get English stopwords
        stop_words = set(stopwords.words('english'))
        
        # Add common web-related stopwords
        stop_words.update([
            'www', 'com', 'org', 'net', 'html', 'http', 'https', 'page', 'site', 'website',
            'home', 'about', 'contact', 'privacy', 'terms', 'policy', 'copyright', 'reserved',
            'rights', 'click', 'here', 'more', 'read', 'view', 'see', 'get', 'new', 'best',
            'top', 'good', 'great', 'free', 'online', 'web', 'internet', 'email', 'phone',
            'address', 'location', 'time', 'date', 'year', 'day', 'today', 'now', 'menu',
            'navigation', 'footer', 'header', 'sidebar', 'content', 'main', 'search', 'find',
            'login', 'register', 'signup', 'sign', 'submit', 'button', 'link', 'back', 'next',
            'previous', 'first', 'last', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
            'eight', 'nine', 'ten', 'also', 'may', 'will', 'can', 'could', 'would', 'should',
            'must', 'need', 'want', 'like', 'use', 'used', 'using', 'make', 'made', 'way',
            'take', 'go', 'come', 'know', 'think', 'say', 'said', 'tell', 'ask', 'give',
            'work', 'look', 'seem', 'try', 'keep', 'let', 'put', 'end', 'turn', 'start',
            'show', 'play', 'run', 'move', 'live', 'believe', 'hold', 'bring', 'happen',
            'write', 'provide', 'sit', 'stand', 'lose', 'add', 'change', 'follow', 'act',
            'why', 'how', 'what', 'where', 'when', 'who', 'which', 'every', 'any', 'some',
            'all', 'each', 'most', 'other', 'another', 'such', 'only', 'own', 'same', 'few',
            'many', 'much', 'long', 'right', 'still', 'old', 'well', 'large', 'small', 'big',
            'high', 'low', 'open', 'public', 'bad', 'different', 'able', 'own', 'under', 'last',
            'never', 'after', 'back', 'other', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'has', 'more', 'go', 'no', 'way',
            'could', 'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now', 'find',
            'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
        ])
        
        # Tokenize the text
        tokens = word_tokenize(text)
        
        # Filter tokens: remove stopwords, short words, and non-alphabetic tokens
        keywords = [
            word for word in tokens 
            if word.lower() not in stop_words 
            and len(word) > 2 
            and word.isalpha()
            and not word.isdigit()
        ]
        
        # Count frequency of keywords
        keyword_freq = Counter(keywords)
        
        # Get most common keywords
        common_keywords = keyword_freq.most_common(max_keywords * 2)  # Get more to filter better
        
        # Filter out very short or very common generic words
        filtered_keywords = []
        for keyword, freq in common_keywords:
            if len(keyword) >= 3 and freq >= 2:  # Must appear at least twice
                filtered_keywords.append(keyword)
        
        # Return top keywords
        return filtered_keywords[:max_keywords]
        
    except Exception as e:
        # Fallback to simple word extraction if NLTK fails
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(max_keywords) if freq >= 2]

def generate_meta_keywords_html(keywords):
    """Generate HTML meta keywords tag."""
    if not keywords:
        return ""
    
    keywords_str = ", ".join(keywords)
    return f'<meta name="keywords" content="{keywords_str}">'

def analyze_keyword_density(text, keywords):
    """Analyze keyword density for the generated keywords."""
    if not text or not keywords:
        return {}
    
    word_count = len(text.split())
    density_analysis = {}
    
    for keyword in keywords:
        keyword_count = text.lower().count(keyword.lower())
        density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        density_analysis[keyword] = {
            'count': keyword_count,
            'density': round(density, 2)
        }
    
    return density_analysis

def get_keyword_recommendations(keywords, density_analysis):
    """Provide recommendations for keyword optimization."""
    recommendations = []
    
    if not keywords:
        recommendations.append("No suitable keywords found. Consider adding more descriptive content to your page.")
        return recommendations
    
    if len(keywords) < 5:
        recommendations.append("Consider adding more relevant keywords. Aim for 5-15 keywords that represent your content.")
    
    if len(keywords) > 20:
        recommendations.append("You have many keywords. Consider focusing on the most relevant 10-15 keywords.")
    
    # Check keyword density
    for keyword, data in density_analysis.items():
        if data['density'] > 3:
            recommendations.append(f"Keyword '{keyword}' has high density ({data['density']}%). Consider reducing usage to avoid over-optimization.")
        elif data['density'] < 0.5:
            recommendations.append(f"Keyword '{keyword}' has low density ({data['density']}%). Consider using it more naturally in your content.")
    
    if not recommendations:
        recommendations.append("Your keyword usage appears to be well-balanced.")
    
    return recommendations

def analyze(response, soup):
    """Analyze and generate meta keywords for the webpage."""
    try:
        # Check for existing meta keywords
        existing_keywords = get_existing_meta_keywords(soup)
        
        # Extract text content
        text_content = extract_text_content(soup)
        
        # Generate new keywords from content
        generated_keywords = extract_keywords_from_text(text_content)
        
        # Analyze keyword density
        keywords_to_analyze = existing_keywords if existing_keywords else generated_keywords
        density_analysis = analyze_keyword_density(text_content, keywords_to_analyze)
        
        # Generate HTML tag
        html_tag = generate_meta_keywords_html(generated_keywords)
        
        # Get recommendations
        recommendations = get_keyword_recommendations(generated_keywords, density_analysis)
        
        # Determine status
        if existing_keywords:
            if len(existing_keywords) < 5:
                status = "warning"
            elif len(existing_keywords) > 20:
                status = "warning"
            else:
                status = "good"
        else:
            status = "bad"  # No meta keywords exist
        
        return {
            'Existing Keywords': {
                'Present': bool(existing_keywords),
                'Keywords': existing_keywords if existing_keywords else "None found",
                'Count': len(existing_keywords) if existing_keywords else 0,
                'Status': status
            },
            'Generated Keywords': {
                'Keywords': generated_keywords,
                'Count': len(generated_keywords),
                'HTML Tag': html_tag,
                'Status': "good" if generated_keywords else "bad"
            },
            'Keyword Density': density_analysis,
            'Recommendations': recommendations,
            'Overall Status': status
        }
        
    except Exception as e:
        return {
            'Error': f"Failed to analyze meta keywords: {str(e)}",
            'Status': "error"
        }
