"""
AI Recommendations Module
Provides AI-powered content and SEO recommendations.
"""

from bs4 import BeautifulSoup
import requests
import re
from collections import defaultdict

def analyze_content_structure(soup):
    """Analyze content structure and provide recommendations."""
    recommendations = []
    
    # Check heading structure
    headings = defaultdict(list)
    for i in range(1, 7):
        headings[f'h{i}'] = soup.find_all(f'h{i}')
    
    if not headings['h1']:
        recommendations.append({
            'type': 'critical',
            'aspect': 'headings',
            'message': 'No H1 heading found. Add a primary heading to improve SEO.',
            'impact': 'high'
        })
    elif len(headings['h1']) > 1:
        recommendations.append({
            'type': 'warning',
            'aspect': 'headings',
            'message': 'Multiple H1 headings found. Consider using only one H1 heading.',
            'impact': 'medium'
        })
    
    # Check content length
    paragraphs = soup.find_all('p')
    total_text = ' '.join(p.get_text() for p in paragraphs)
    word_count = len(total_text.split())
    
    if word_count < 300:
        recommendations.append({
            'type': 'warning',
            'aspect': 'content_length',
            'message': 'Content is too short. Aim for at least 300 words for better SEO.',
            'impact': 'high'
        })
    
    # Check image optimization
    images = soup.find_all('img')
    for img in images:
        if not img.get('alt'):
            recommendations.append({
                'type': 'warning',
                'aspect': 'images',
                'message': f'Image missing alt text: {img.get("src", "unknown")}',
                'impact': 'medium'
            })
    
    # Check internal linking
    links = soup.find_all('a')
    internal_links = [link for link in links if not link.get('href', '').startswith(('http', 'https'))]
    if len(internal_links) < 2:
        recommendations.append({
            'type': 'suggestion',
            'aspect': 'internal_linking',
            'message': 'Add more internal links to improve site structure.',
            'impact': 'medium'
        })
    
    return recommendations

def analyze_readability(text):
    """Analyze text readability and provide recommendations."""
    sentences = re.split(r'[.!?]+', text)
    words_per_sentence = sum(len(s.split()) for s in sentences if s.strip()) / len(sentences) if sentences else 0
    
    recommendations = []
    
    if words_per_sentence > 20:
        recommendations.append({
            'type': 'suggestion',
            'aspect': 'readability',
            'message': 'Sentences are too long. Consider breaking them down for better readability.',
            'impact': 'medium'
        })
    
    # Check paragraph length
    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs):
        if len(p.split()) > 100:
            recommendations.append({
                'type': 'suggestion',
                'aspect': 'readability',
                'message': f'Paragraph {i+1} is too long. Consider breaking it into smaller paragraphs.',
                'impact': 'low'
            })
    
    return recommendations

def get_ai_recommendations(url):
    """Get AI-powered recommendations for a URL."""
    try:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get content recommendations
        content_recommendations = analyze_content_structure(soup)
        
        # Get readability recommendations
        text = soup.get_text()
        readability_recommendations = analyze_readability(text)
        
        # Combine all recommendations
        all_recommendations = content_recommendations + readability_recommendations
        
        # Prioritize recommendations
        prioritized_recommendations = {
            'critical': [r for r in all_recommendations if r['type'] == 'critical'],
            'warnings': [r for r in all_recommendations if r['type'] == 'warning'],
            'suggestions': [r for r in all_recommendations if r['type'] == 'suggestion']
        }
        
        return {
            'status': 'success',
            'recommendations': prioritized_recommendations,
            'summary': {
                'critical_issues': len(prioritized_recommendations['critical']),
                'warnings': len(prioritized_recommendations['warnings']),
                'suggestions': len(prioritized_recommendations['suggestions'])
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 