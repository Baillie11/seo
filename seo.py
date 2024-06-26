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
    
    if "Technical SEO" in categories:
        try:
            response = requests.get(url, timeout=10)  # Timeout after 10 seconds
            load_time = response.elapsed.total_seconds()
            seo_data['Page Load Time'] = f"{load_time} seconds"
            
            # Assign a rating based on the load time
            if load_time < 2:
                seo_data['Load Time Rating'] = "Good"
            elif load_time < 5:
                seo_data['Load Time Rating'] = "Average"
            else:
                seo_data['Load Time Rating'] = "Poor"
                
        except requests.exceptions.RequestException as e:
            seo_data['Page Load Time'] = f"Failed to load page: {str(e)}"
            seo_data['Load Time Rating'] = "Error"

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
    c.drawImage(logo_path, (width - 200) / 2, height - 80, width=200, height=50, preserveAspectRatio=True, mask='auto')
    
    # Add header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, "SEO Analysis Report")
    
    # Technical SEO Analysis section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 140, "Technical SEO Analysis:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 160, f"Page Load Time: {seo_data.get('Page Load Time', 'Not available')}")

    # Separate column for rating, in italics
    c.setFont("Helvetica-Oblique", 12)  # Italic font for rating
    c.drawString(250, height - 160, f"Rating: {seo_data.get('Load Time Rating', 'Not rated')}")

    c.save()
    return filename

    # Prepare to add text
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 140, "SEO Analysis Report")

    # Example of adding additional text below
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 160, f"Website: {seo_data['URL']}")
    c.drawString(30, height - 180, f"Report Date: {datetime.now().strftime('%Y-%m-%d')}")

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
