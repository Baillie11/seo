"""
Keyword Analysis Module
Provides keyword suggestions and ranking analysis.
"""

from collections import Counter
import re
from bs4 import BeautifulSoup
import requests

# Create the download function first
def download_nltk_data():
    """Download required NLTK data."""
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")

# Initialize NLTK with error handling
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    download_nltk_data()
except ImportError:
    print("NLTK not installed. Running pip install nltk...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'nltk'])
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    download_nltk_data()

def extract_keywords(text):
    """Extract keywords from text, removing common words."""
    try:
        # Tokenize and convert to lowercase
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens 
                   if word.isalpha() and 
                   word not in stop_words and 
                   len(word) > 2]
        
        return Counter(keywords)
    except Exception as e:
        print(f"Error in keyword extraction: {str(e)}")
        # Fallback to simple word splitting if NLTK fails
        words = text.lower().split()
        return Counter([w for w in words if len(w) > 2])

def analyze_keyword_density(soup):
    """Analyze keyword density in the content."""
    try:
        # Get all text content
        text = soup.get_text()
        
        # Extract keywords and their frequencies
        keyword_freq = extract_keywords(text)
        total_words = len(text.split())  # Simplified word count for robustness
        
        # Calculate density
        keyword_density = {
            word: (count / total_words) * 100 
            for word, count in keyword_freq.most_common(20)
        }
        
        return {
            'total_words': total_words,
            'keyword_density': keyword_density,
            'top_keywords': list(keyword_density.keys())
        }
    except Exception as e:
        print(f"Error in keyword density analysis: {str(e)}")
        return {
            'total_words': 0,
            'keyword_density': {},
            'top_keywords': []
        }

def suggest_keywords(main_keywords, soup):
    """Suggest related keywords based on content analysis."""
    try:
        # Extract all keywords from content
        content_keywords = extract_keywords(soup.get_text())
        
        # Find keywords that often appear near the main keywords
        related_keywords = set()
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text().lower()
            for keyword in main_keywords:
                if keyword.lower() in text:
                    # Get words around the keyword
                    words = extract_keywords(text)
                    related_keywords.update(words.keys())
        
        # Remove the main keywords from related keywords
        related_keywords = related_keywords - set(main_keywords)
        
        return list(related_keywords)[:10]
    except Exception as e:
        print(f"Error in keyword suggestion: {str(e)}")
        return []

def get_keyword_suggestions(url, main_keywords):
    """Get keyword suggestions for a URL."""
    try:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Analyze current keyword usage
        density_analysis = analyze_keyword_density(soup)
        
        # Get related keyword suggestions
        related_keywords = suggest_keywords(main_keywords, soup)
        
        return {
            'status': 'success',
            'current_keywords': density_analysis,
            'suggested_keywords': related_keywords,
            'recommendations': {
                'underused_keywords': [k for k in main_keywords 
                                     if k.lower() not in density_analysis['top_keywords']],
                'overused_keywords': [k for k, v in density_analysis['keyword_density'].items() 
                                    if v > 5.0]  # More than 5% density might be keyword stuffing
            }
        }
        
    except Exception as e:
        print(f"Error in keyword analysis: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'current_keywords': {
                'total_words': 0,
                'keyword_density': {},
                'top_keywords': []
            },
            'suggested_keywords': [],
            'recommendations': {
                'underused_keywords': [],
                'overused_keywords': []
            }
        } 