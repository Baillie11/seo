"""
Main Routes
Handles SEO analysis and report generation.
"""

from flask import render_template, request, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from . import main
from .. import db
from ..models.analysis import Analysis
from ..modules import (
    technical_seo,
    on_page_seo,
    content_seo,
    user_experience,
    security,
    schema_markup,
    advanced_content
)
from ..utils.pdf_generator import create_report

def perform_seo_analysis(url, categories):
    """Coordinate the SEO analysis across all selected categories."""
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        seo_data['URL'] = url

    try:
        # Make initial request to get the page content
        response = requests.get(url, timeout=20, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Run selected analyses
        if "Technical SEO" in categories:
            seo_data['Technical SEO'] = technical_seo.analyze(response, soup)
            
        if "On-Page SEO" in categories:
            seo_data['On-Page SEO'] = on_page_seo.analyze(response, soup)
            
        if "Content SEO" in categories:
            seo_data['Content SEO'] = content_seo.analyze(response, soup)
            
        if "User Experience" in categories:
            seo_data['User Experience'] = user_experience.analyze(response, soup, url)
            
        if "Security" in categories:
            seo_data['Security'] = security.analyze(response, url)
            
        if "Schema Markup" in categories:
            seo_data['Schema Markup'] = schema_markup.analyze(response, soup)
            
        if "Advanced Content" in categories:
            seo_data['Advanced Content'] = advanced_content.analyze(response, soup)

    except requests.exceptions.SSLError:
        # Try HTTP if HTTPS fails
        try:
            http_url = url.replace('https://', 'http://')
            response = requests.get(http_url, timeout=20, allow_redirects=True)
            seo_data['Security Warning'] = "Website is using unsecure HTTP protocol"
            soup = BeautifulSoup(response.text, 'html.parser')
            # Run the analyses again...
        except:
            seo_data['Error'] = "Could not connect to website via HTTP or HTTPS"
            
    except requests.exceptions.Timeout:
        seo_data['Error'] = "Website took too long to respond (timeout: 20 seconds)"
        
    except requests.exceptions.ConnectionError:
        seo_data['Error'] = "Could not establish connection to the website"
        
    except requests.exceptions.RequestException as e:
        seo_data['Error'] = f"Failed to analyze the website: {str(e)}"

    return seo_data

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        url = request.form['url']
        selected_categories = request.form.getlist('categories')
        seo_data = perform_seo_analysis(url, selected_categories)
        
        # Create PDF report
        pdf_filename = create_report(seo_data, selected_categories)
        
        # Save analysis to database
        analysis = Analysis(
            url=url,
            user_id=current_user.id,
            report_path=pdf_filename,
            categories=','.join(selected_categories)
        )
        db.session.add(analysis)
        db.session.commit()
        
        return render_template('report.html', 
                             seo_data=seo_data, 
                             pdf_filename=pdf_filename, 
                             categories=selected_categories)
    return render_template('index.html')

@main.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory('.', filename, as_attachment=True) 