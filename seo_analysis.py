from bs4 import BeautifulSoup
import requests
from datetime import datetime

def perform_seo_analysis(url, categories, keywords=[]):
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    try:
        response = requests.get(url, timeout=10)  # Timeout after 10 seconds
        soup = BeautifulSoup(response.text, 'html.parser')

        if "Technical SEO" in categories:
            load_time = response.elapsed.total_seconds()
            seo_data['Page Load Time'] = f"{load_time} seconds"
            if load_time < 2:
                seo_data['Load Time Rating'] = "Good"
            elif load_time < 5:
                seo_data['Load Time Rating'] = "Average"
            else:
                seo_data['Load Time Rating'] = "Poor"
        
        if "On-Page SEO" in categories:
            title_tag = soup.find('title').string if soup.find('title') else "No Title Found"
            seo_data['Title Tag'] = title_tag
            seo_data['Title Character Count'] = len(title_tag)  # Store the character count
            
            # Check the length of the title tag
            if len(title_tag) < 50 or len(title_tag) > 60:
                seo_data['Title Length Status'] = "Incorrect Length (Recommended: 50-60 characters)"
            else:
                seo_data['Title Length Status'] = "Good Length"

            # Check for presence of keywords
            if keywords:
                seo_data['Keyword Presence'] = "Keywords found" if any(keyword.lower() in title_tag.lower() for keyword in keywords) else "No Keywords found"

    except requests.exceptions.RequestException as e:
        seo_data['Error'] = str(e)

    return seo_data
