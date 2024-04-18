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
        # Measure page load time
        try:
            response = requests.get(url, timeout=10)  # Timeout after 10 seconds
            load_time = response.elapsed.total_seconds()
            seo_data['Page Load Time'] = f"{load_time} seconds"
        except requests.exceptions.RequestException as e:
            seo_data['Page Load Time'] = f"Failed to load page: {str(e)}"
    
    return seo_data

# Function to create a PDF report with logo and formatted title
def create_pdf_report(seo_data, categories, filename=None):
    if not filename:
        # Remove 'http://' or 'https://' from the URL
        clean_url = seo_data['URL'].replace('http://', '').replace('https://', '')
        # Sanitize the URL to create a valid filename component
        sanitized_url = re.sub(r'[^\w\s-]', '', clean_url).replace(' ', '_').replace('.', '_')
        # Construct the filename using the format SEO_Report_for_<URL>
        filename = f'SEO_Report_for_{sanitized_url}.pdf'

    width, height = A4
    c = canvas.Canvas(filename, pagesize=A4)
    
    # Add the logo at the top center
    logo_path = './static/logo.jpg'
    c.drawImage(logo_path, (width - 200) / 2, height - 120, width=200, height=100, preserveAspectRatio=True, mask='auto')

    # Header Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 150, "SEO Analysis Report")

    # Technical SEO Analysis Section
    c.setFont("Helvetica-Bold", 14)  # Bold for section heading
    c.drawString(30, height - 180, "Technical SEO Analysis:")
    
    # Check if Page Load Time is in the data and display it
    if 'Page Load Time' in seo_data:
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 200, f"Page Load Time: {seo_data['Page Load Time']}")

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
