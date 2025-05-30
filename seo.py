from flask import Flask, render_template, request, send_from_directory
from bs4 import BeautifulSoup
import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from datetime import datetime
import re


app = Flask(__name__)

# Function to perform SEO analysis
def perform_seo_analysis(url, categories):
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        seo_data['URL'] = url

    try:
        # Make initial request to get the page content
        response = requests.get(url, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "Technical SEO" in categories:
            # Technical SEO Analysis
            load_time = response.elapsed.total_seconds()
            seo_data['Technical SEO'] = {
                'Page Load Time': f"{load_time} seconds",
                'Status Code': response.status_code,
                'Response Size': f"{len(response.content) / 1024:.2f} KB"
            }
            
            # Load time rating
            if load_time < 2:
                seo_data['Technical SEO']['Load Time Rating'] = "Good"
            elif load_time < 5:
                seo_data['Technical SEO']['Load Time Rating'] = "Average"
            else:
                seo_data['Technical SEO']['Load Time Rating'] = "Poor"

        if "On-Page SEO" in categories:
            # On-Page SEO Analysis
            title_tag = soup.find('title')
            meta_description = soup.find('meta', attrs={'name': 'description'})
            h1_tags = soup.find_all('h1')
            
            seo_data['On-Page SEO'] = {
                'Title': title_tag.text if title_tag else "No title tag found",
                'Title Length': len(title_tag.text) if title_tag else 0,
                'Meta Description': meta_description['content'] if meta_description else "No meta description found",
                'Meta Description Length': len(meta_description['content']) if meta_description else 0,
                'H1 Count': len(h1_tags),
                'H1 Tags': [tag.text for tag in h1_tags[:3]]  # First 3 H1 tags
            }

        if "Content SEO" in categories:
            # Content SEO Analysis
            paragraphs = soup.find_all('p')
            images = soup.find_all('img')
            
            seo_data['Content SEO'] = {
                'Word Count': len(response.text.split()),
                'Paragraph Count': len(paragraphs),
                'Image Count': len(images),
                'Images with Alt Text': len([img for img in images if img.get('alt')])
            }

        if "User Experience" in categories:
            # User Experience Analysis
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            links = soup.find_all('a')
            
            seo_data['User Experience'] = {
                'Mobile Responsive': "Yes" if viewport_meta else "No",
                'Total Links': len(links),
                'Internal Links': len([link for link in links if link.get('href', '').startswith(('/', url))]),
                'External Links': len([link for link in links if link.get('href', '').startswith('http')])
            }

        if "Security" in categories:
            # Security Analysis
            security_headers = {
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security', 'Not set'),
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', 'Not set'),
                'X-Frame-Options': response.headers.get('X-Frame-Options', 'Not set'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy', 'Not set')
            }
            
            seo_data['Security'] = {
                'HTTPS': url.startswith('https://'),
                'Security Headers': security_headers
            }

        if "Schema Markup" in categories:
            # Schema Markup Analysis
            schema_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            social_meta = {
                'og:title': soup.find('meta', {'property': 'og:title'}),
                'og:description': soup.find('meta', {'property': 'og:description'}),
                'og:image': soup.find('meta', {'property': 'og:image'}),
                'twitter:card': soup.find('meta', {'name': 'twitter:card'}),
                'twitter:title': soup.find('meta', {'name': 'twitter:title'})
            }
            
            seo_data['Schema Markup'] = {
                'JSON-LD Scripts': len(schema_scripts),
                'Schema Types': [script.string.split('"@type":')[1].split('"')[1] for script in schema_scripts if script.string and '"@type":' in script.string],
                'OpenGraph Tags': {k: v['content'] if v else 'Not found' for k, v in social_meta.items() if k.startswith('og:')},
                'Twitter Cards': {k: v['content'] if v else 'Not found' for k, v in social_meta.items() if k.startswith('twitter:')}
            }

        if "Advanced Content" in categories:
            # Advanced Content Analysis
            all_text = soup.get_text()
            words = all_text.lower().split()
            word_count = len(words)
            
            # Keyword density (top 5 words, excluding common words)
            common_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'])
            word_freq = {}
            for word in words:
                if word not in common_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Check heading hierarchy
            headings = {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4')),
                'h5': len(soup.find_all('h5')),
                'h6': len(soup.find_all('h6'))
            }
            
            # Check for broken links
            links = soup.find_all('a')
            broken_links = []
            for link in links[:10]:  # Check first 10 links to avoid too many requests
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
            
            seo_data['Advanced Content'] = {
                'Word Count': word_count,
                'Top Keywords': sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5],
                'Heading Structure': headings,
                'Content-to-HTML Ratio': f"{content_ratio:.2f}%",
                'Broken Links Found': len(broken_links),
                'Broken Links': broken_links[:5] if broken_links else "None found"
            }

    except requests.exceptions.SSLError:
        # Try HTTP if HTTPS fails
        try:
            http_url = url.replace('https://', 'http://')
            response = requests.get(http_url, timeout=20, allow_redirects=True)
            seo_data['Security Warning'] = "Website is using unsecure HTTP protocol"
            # Perform the same analysis with HTTP response
            # ... (repeat the analysis code)
        except:
            seo_data['Error'] = "Could not connect to website via HTTP or HTTPS"
            
    except requests.exceptions.Timeout:
        seo_data['Error'] = "Website took too long to respond (timeout: 20 seconds)"
        
    except requests.exceptions.ConnectionError:
        seo_data['Error'] = "Could not establish connection to the website"
        
    except requests.exceptions.RequestException as e:
        seo_data['Error'] = f"Failed to analyze the website: {str(e)}"

    return seo_data

# Function to create a PDF report with logo and formatted title
def create_pdf_report(seo_data, categories, filename=None):
    if not filename:
        clean_url = seo_data['URL'].replace('http://', '').replace('https://', '')
        sanitized_url = re.sub(r'[^\w\s-]', '', clean_url).replace(' ', '_').replace('.', '_')
        filename = f"SEO_Report_for_{sanitized_url}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Add logo
    logo_path = './static/logo.jpg'
    try:
        c.drawImage(logo_path, (width - 200) / 2, height - 80, width=200, height=50, preserveAspectRatio=True, mask='auto')
    except:
        # If logo fails to load, just skip it
        pass
    
    # Add header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, "SEO Analysis Report")
    
    # Add URL and date
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 130, f"URL: {seo_data['URL']}")
    c.drawString(30, height - 150, f"Analysis Date: {seo_data['Analysis Date']}")
    
    y_position = height - 180

    # Check for errors first
    if 'Error' in seo_data:
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.red)
        c.drawString(30, y_position, "Error:")
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position - 20, seo_data['Error'])
        return filename

    # Draw each category
    for category in categories:
        if category in seo_data:
            # Category header
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.black)
            c.drawString(30, y_position, f"{category}:")
            y_position -= 25
            
            # Category details
            c.setFont("Helvetica", 12)
            for key, value in seo_data[category].items():
                if isinstance(value, dict):
                    # Handle nested dictionaries (like security headers)
                    c.drawString(50, y_position, f"{key}:")
                    y_position -= 20
                    for subkey, subvalue in value.items():
                        c.drawString(70, y_position, f"{subkey}: {subvalue}")
                        y_position -= 20
                elif isinstance(value, list):
                    # Handle lists (like H1 tags)
                    c.drawString(50, y_position, f"{key}:")
                    y_position -= 20
                    for item in value:
                        c.drawString(70, y_position, f"- {item}")
                        y_position -= 20
                else:
                    # Handle simple key-value pairs
                    c.drawString(50, y_position, f"{key}: {value}")
                    y_position -= 20
            
            y_position -= 10  # Add space between categories
            
            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = height - 50

    # Add any warnings
    if 'Security Warning' in seo_data:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.red)
        c.drawString(30, y_position, f"Security Warning: {seo_data['Security Warning']}")

    c.save()
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        selected_categories = request.form.getlist('categories')  # Gets the list of selected categories
        seo_data = perform_seo_analysis(url, selected_categories)  # Assuming this function can handle categories
        pdf_filename = create_pdf_report(seo_data, selected_categories)  # Pass categories here
        return render_template('report.html', seo_data=seo_data, pdf_filename=pdf_filename, categories=selected_categories)
    return render_template('index.html')


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
