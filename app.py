"""
Main SEO Analysis Application
Coordinates all SEO analysis modules and handles web requests.
"""

from flask import Flask, render_template, request, send_from_directory, jsonify, flash, redirect, url_for
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
from urllib.parse import urlparse
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from dotenv import load_dotenv
import urllib3
import json
import time
import random
import traceback
from urllib.parse import urljoin
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import sys
from io import StringIO
import contextlib
import tempfile
import shutil
from pathlib import Path
import platform
import socket
import ssl
from urllib.error import URLError
import validators
import sqlite3

# Import models and database
from models import db
from models.user import User
from models.analysis import Analysis

# Import analysis modules
from modules import (
    technical_seo,
    on_page_seo,
    content_seo,
    user_experience,
    security,
    schema_markup,
    advanced_content,
    rank_analysis,
    meta_keywords
)

# Import utilities
from utils.pdf_generator import create_report
from modules.enhanced_analysis.competitor import compare_websites
from modules.enhanced_analysis.keywords import get_keyword_suggestions
from modules.enhanced_analysis.ai_recommendations import get_ai_recommendations
from modules.enhanced_analysis.mobile_testing import analyze_mobile_friendliness
from modules.enhanced_analysis.speed_insights import analyze_speed

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///seo_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('usage_tracking.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            scan_type TEXT,
            result_summary TEXT
        )
    ''')
    
    # Create subscribers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            feature_updates BOOLEAN DEFAULT 1,
            seo_tips BOOLEAN DEFAULT 1,
            subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_scan(url, scan_type, result_summary):
    conn = sqlite3.connect('usage_tracking.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO scan_usage (url, scan_type, result_summary)
        VALUES (?, ?, ?)
    ''', (url, scan_type, result_summary))
    conn.commit()
    conn.close()

def get_usage_stats():
    conn = sqlite3.connect('usage_tracking.db')
    c = conn.cursor()
    
    # Get total scans
    c.execute('SELECT COUNT(*) FROM scan_usage')
    total_scans = c.fetchone()[0]
    
    # Get scans by type
    c.execute('SELECT scan_type, COUNT(*) FROM scan_usage GROUP BY scan_type')
    scans_by_type = dict(c.fetchall())
    
    # Get recent scans
    c.execute('SELECT url, timestamp, scan_type FROM scan_usage ORDER BY timestamp DESC LIMIT 10')
    recent_scans = c.fetchall()
    
    conn.close()
    
    return {
        'total_scans': total_scans,
        'scans_by_type': scans_by_type,
        'recent_scans': recent_scans
    }

# Initialize database when app starts
init_db()

def perform_seo_analysis(url, categories):
    """Coordinate the SEO analysis across all selected categories."""
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    # URL validation check
    if not validators.url(url):
        seo_data['Error'] = "Invalid URL format. Please enter a valid URL (e.g., https://example.com)"
        return seo_data
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        seo_data['URL'] = url

    try:
        # Check if website is accessible
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code >= 400:
            seo_data['Error'] = f"Website is not accessible. Status code: {response.status_code}"
            return seo_data
            
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
            
        if "Meta Keywords" in categories:
            seo_data['Meta Keywords'] = meta_keywords.analyze(response, soup)

        # Always include ranking analysis
        seo_data['Ranking Analysis'] = rank_analysis.analyze(url)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        selected_categories = request.form.getlist('categories')
        
        # URL validation check
        if not validators.url(url):
            flash('Invalid URL format. Please enter a valid URL (e.g., https://example.com)', 'error')
            return redirect(url_for('index'))
            
        # Check if website is accessible
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                flash(f'Website is not accessible. Status code: {response.status_code}', 'error')
                return redirect(url_for('index'))
        except requests.RequestException as e:
            flash(f'Cannot connect to website: {str(e)}', 'error')
            return redirect(url_for('index'))
            
        # If we get here, the URL is valid and the site is accessible
        flash('Website is valid and accessible. Starting analysis...', 'success')
        
        # Perform basic SEO analysis
        seo_data = perform_seo_analysis(url, selected_categories)
        
        # Check if enhanced analysis is enabled
        if request.form.get('enhanced_analysis'):
            # Process competitor URLs
            competitor_urls = [url.strip() for url in request.form.get('competitor_urls', '').split('\n') if url.strip()]
            
            # Process keywords
            keywords = [kw.strip() for kw in request.form.get('keywords', '').split(',') if kw.strip()]
            
            try:
                # Run enhanced analyses
                enhanced_results = {}
                
                if competitor_urls:
                    comp_analysis = compare_websites(url, competitor_urls)
                    if isinstance(comp_analysis, dict) and comp_analysis.get('status') == 'error':
                        enhanced_results['competitor_error'] = comp_analysis.get('message', 'Failed to analyze competitors')
                    else:
                        enhanced_results['competitor_analysis'] = comp_analysis
                
                if keywords:
                    kw_analysis = get_keyword_suggestions(url, keywords)
                    if isinstance(kw_analysis, dict) and kw_analysis.get('status') == 'error':
                        enhanced_results['keyword_error'] = kw_analysis.get('message', 'Failed to analyze keywords')
                    else:
                        enhanced_results['keyword_suggestions'] = kw_analysis
                
                ai_rec = get_ai_recommendations(url)
                if isinstance(ai_rec, dict) and ai_rec.get('status') == 'error':
                    enhanced_results['ai_error'] = ai_rec.get('message', 'Failed to generate AI recommendations')
                else:
                    enhanced_results['ai_recommendations'] = ai_rec
                
                mobile = analyze_mobile_friendliness(url)
                if isinstance(mobile, dict) and mobile.get('status') == 'error':
                    enhanced_results['mobile_error'] = mobile.get('message', 'Failed to analyze mobile friendliness')
                else:
                    enhanced_results['mobile_analysis'] = mobile
                
                speed = analyze_speed(url)
                if isinstance(speed, dict) and speed.get('status') == 'error':
                    enhanced_results['speed_error'] = speed.get('message', 'Failed to analyze site speed')
                else:
                    enhanced_results['speed_insights'] = speed
                
                # Add enhanced results to seo_data
                seo_data['enhanced_results'] = enhanced_results
                
            except Exception as e:
                seo_data['enhanced_error'] = str(e)
        
        # Generate PDF report
        pdf_filename = None
        pdf_error = None
        try:
            logger.info("Attempting to generate PDF report")
            pdf_filename = create_report(seo_data, selected_categories)
            if pdf_filename:
                logger.info(f"PDF report generated successfully: {pdf_filename}")
                # Verify the file exists
                reports_dir = os.path.join(app.root_path, 'reports')
                if not os.path.exists(os.path.join(reports_dir, pdf_filename)):
                    raise FileNotFoundError(f"Generated PDF file not found: {pdf_filename}")
            else:
                raise ValueError("PDF generation returned None")
        except Exception as e:
            error_msg = f"Failed to generate PDF report: {str(e)}"
            logger.error(error_msg)
            pdf_error = error_msg
            flash("Failed to generate PDF report. You can still view the analysis results online.", "warning")
        
        # Log the scan
        result_summary = "Scan completed successfully"  # Replace with actual summary
        log_scan(url, 'full', result_summary)
        
        return render_template('report.html', 
                             seo_data=seo_data, 
                             pdf_filename=pdf_filename,
                             pdf_error=pdf_error,
                             categories=selected_categories)
    
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    """Handle file downloads with proper error handling."""
    if not filename:
        return "No filename specified", 400
    
    try:
        # Get the reports directory path
        reports_dir = os.path.join(app.root_path, 'reports')
        
        # Create the reports directory if it doesn't exist
        os.makedirs(reports_dir, exist_ok=True)
        
        # Check if file exists in the reports directory
        if not os.path.exists(os.path.join(reports_dir, filename)):
            app.logger.error(f"File not found: {filename}")
            return "File not found", 404
        
        return send_from_directory(reports_dir, filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading file {filename}: {str(e)}")
        return "Error downloading file", 500

@app.route('/api/enhanced-analysis', methods=['POST'])
def enhanced_analysis():
    """Endpoint for enhanced SEO analysis."""
    data = request.get_json()
    url = data.get('url')
    competitor_urls = data.get('competitor_urls', [])
    main_keywords = data.get('keywords', [])
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Run all enhanced analyses in parallel
        results = {
            'competitor_analysis': compare_websites(url, competitor_urls),
            'keyword_suggestions': get_keyword_suggestions(url, main_keywords),
            'ai_recommendations': get_ai_recommendations(url),
            'mobile_analysis': analyze_mobile_friendliness(url),
            'speed_insights': analyze_speed(url)
        }
        
        # Log the scan
        result_summary = "Scan completed successfully"  # Replace with actual summary
        log_scan(url, 'enhanced', result_summary)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/create_robots_txt', methods=['POST'])
def create_robots_txt():
    """Create a robots.txt file for the specified domain."""
    try:
        data = request.get_json()
        url = data.get('url')
        content = data.get('content')
        
        if not url or not content:
            return jsonify({
                'status': 'error',
                'message': 'URL and content are required'
            }), 400
            
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Make a PUT request to create/update robots.txt
        robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
        
        # First check if we have write access
        try:
            response = requests.put(robots_url, data=content)
            if response.status_code in [200, 201, 204]:
                return jsonify({
                    'status': 'success',
                    'message': 'robots.txt created successfully'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to create robots.txt. Server returned status code: {response.status_code}',
                    'details': 'You may need to manually create the file using the suggested content.'
                }), 400
        except requests.exceptions.RequestException as e:
            return jsonify({
                'status': 'error',
                'message': 'Could not create robots.txt file automatically',
                'details': 'You may need to manually create the file using the suggested content.',
                'error': str(e)
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An error occurred',
            'error': str(e)
        }), 500

@app.route('/create_sitemap', methods=['POST'])
def create_sitemap():
    """Create a sitemap.xml file for the specified domain."""
    try:
        data = request.get_json()
        url = data.get('url')
        content = data.get('content')
        
        if not url or not content:
            return jsonify({
                'status': 'error',
                'message': 'URL and content are required'
            }), 400
            
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Make a PUT request to create/update sitemap.xml
        sitemap_url = f"{parsed_url.scheme}://{domain}/sitemap.xml"
        
        # First check if we have write access
        try:
            response = requests.put(sitemap_url, data=content)
            if response.status_code in [200, 201, 204]:
                return jsonify({
                    'status': 'success',
                    'message': 'sitemap.xml created successfully'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to create sitemap.xml. Server returned status code: {response.status_code}',
                    'details': 'You may need to manually create the file using the suggested content.'
                }), 400
        except requests.exceptions.RequestException as e:
            return jsonify({
                'status': 'error',
                'message': 'Could not create sitemap.xml file automatically',
                'details': 'You may need to manually create the file using the suggested content.',
                'error': str(e)
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An error occurred',
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    try:
        url = request.form.get('url', '').strip()
        
        # URL validation check
        if not validators.url(url):
            flash('Invalid URL format. Please enter a valid URL (e.g., https://example.com)', 'error')
            return redirect(url_for('dashboard'))
            
        # Check if website is accessible
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                flash(f'Website is not accessible. Status code: {response.status_code}', 'error')
                return redirect(url_for('dashboard'))
        except requests.RequestException as e:
            flash(f'Cannot connect to website: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
            
        # If we get here, the URL is valid and the site is accessible
        flash('Website is valid and accessible. Starting analysis...', 'success')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get selected categories
        selected_categories = request.form.getlist('categories')
        if not selected_categories:
            selected_categories = ['Technical SEO', 'On-Page SEO', 'Content SEO']
        
        # Perform SEO analysis
        seo_data = perform_seo_analysis(url, selected_categories)
        
        # Generate PDF report
        pdf_filename = None
        pdf_error = None
        try:
            pdf_filename = generate_pdf_report(seo_data, url)
        except Exception as e:
            pdf_error = str(e)
            flash("Failed to generate PDF report. You can still view the analysis results online.", "warning")
        
        # Log the scan
        result_summary = "Scan completed successfully"  # Replace with actual summary
        log_scan(url, 'full', result_summary)
        
        return render_template('report.html', 
                             seo_data=seo_data, 
                             pdf_filename=pdf_filename,
                             pdf_error=pdf_error,
                             categories=selected_categories)
                             
    except Exception as e:
        flash(f"An error occurred during analysis: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/usage-stats')
def usage_stats():
    stats = get_usage_stats()
    return render_template('usage_stats.html', stats=stats)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        feature_updates = data.get('featureUpdates', True)
        seo_tips = data.get('seoTips', True)
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
            
        if not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Please enter a valid email address'}), 400
            
        conn = sqlite3.connect('usage_tracking.db')
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO subscribers (email, feature_updates, seo_tips)
                VALUES (?, ?, ?)
            ''', (email, feature_updates, seo_tips))
            conn.commit()
            return jsonify({
                'success': True,
                'message': 'Thank you for subscribing! We\'ll keep you updated with the latest features.'
            })
        except sqlite3.IntegrityError:
            return jsonify({
                'success': False,
                'message': 'This email is already subscribed.'
            }), 400
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }), 500

@app.route('/admin/subscribers')
def view_subscribers():
    try:
        conn = sqlite3.connect('usage_tracking.db')
        c = conn.cursor()
        
        # Get all subscribers
        c.execute('''
            SELECT id, email, feature_updates, seo_tips, subscribed_at
            FROM subscribers
            ORDER BY subscribed_at DESC
        ''')
        subscribers = c.fetchall()
        
        # Format the data
        formatted_subscribers = []
        for sub in subscribers:
            formatted_subscribers.append({
                'id': sub[0],
                'email': sub[1],
                'feature_updates': bool(sub[2]),
                'seo_tips': bool(sub[3]),
                'subscribed_at': sub[4]
            })
        
        conn.close()
        return render_template('subscribers.html', subscribers=formatted_subscribers)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching subscribers.'
        }), 500

@app.route('/admin/subscribers/<int:subscriber_id>', methods=['DELETE'])
def delete_subscriber(subscriber_id):
    try:
        conn = sqlite3.connect('usage_tracking.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM subscribers WHERE id = ?', (subscriber_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscriber removed successfully.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while removing the subscriber.'
        }), 500

@app.route('/admin/subscribers/<int:subscriber_id>', methods=['PUT'])
def update_subscriber(subscriber_id):
    try:
        data = request.get_json()
        feature_updates = data.get('featureUpdates', True)
        seo_tips = data.get('seoTips', True)
        
        conn = sqlite3.connect('usage_tracking.db')
        c = conn.cursor()
        
        c.execute('''
            UPDATE subscribers
            SET feature_updates = ?, seo_tips = ?
            WHERE id = ?
        ''', (feature_updates, seo_tips, subscriber_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscriber preferences updated successfully.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while updating subscriber preferences.'
        }), 500

@app.route('/meta-generator')
def meta_generator():
    return render_template('meta_generator.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True) 