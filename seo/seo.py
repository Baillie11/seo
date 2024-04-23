from flask import Flask, render_template, request, send_from_directory
from bs4 import BeautifulSoup
import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from datetime import datetime
import re


app = Flask(__name__)

# Function to perform SEO analysis
def perform_seo_analysis(url, categories,keywords=[]):
    seo_data = {'URL': url, 'Analysis Date': datetime.now().strftime("%Y-%m-%d")}
    
    try:
        response = requests.get(url, timeout=10)  # Timeout after 10 seconds
        soup = BeautifulSoup(response.text, 'html.parser')

        if "Technical SEO" in categories:
            load_time = response.elapsed.total_seconds()
            seo_data['Page Load Time'] = f"{load_time} seconds"
            # Assign a rating based on the load time
            if load_time < 2:
                seo_data['Load Time Rating'] = "Good"
            elif load_time < 5:
                seo_data['Load Time Rating'] = "Average"
            else:
                seo_data['Load Time Rating'] = "Poor"

        if "On-Page SEO" in categories:
            title_tag = soup.find('title').string if soup.find('title') else "No Title Found"
            seo_data['Title Tag'] = title_tag
            
            # Check the length of the title tag
            if len(title_tag) < 50 or len(title_tag) > 60:
                seo_data['Title Length Status'] = "Incorrect Length (Recommended: 50-60 characters)"
            else:
                seo_data['Title Length Status'] = "Good Length"

            # Check for presence of keywords
            if keywords:
                if any(keyword.lower() in title_tag.lower() for keyword in keywords):
                    seo_data['Keyword Presence'] = "Keywords found"
                else:
                    seo_data['Keyword Presence'] = "No Keywords found"

    except requests.exceptions.RequestException as e:
        seo_data['Page Load Time'] = f"Failed to load page: {str(e)}"
        seo_data['Load Time Rating'] = "Error"

    return seo_data

# Function to create a PDF report with logo and formatted title
def create_pdf_report(seo_data, categories, filename=None):
    reports_folder = 'reports'
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)

    if not filename:
        clean_url = seo_data['URL'].replace('http://', '').replace('https://', '')
        sanitized_url = re.sub(r'[^\w\s-]', '', clean_url).replace(' ', '_').replace('.', '_')
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"SEO_Report_for-{sanitized_url}_{current_date}.pdf"

    full_path = os.path.join(reports_folder, filename)
    c = canvas.Canvas(full_path, pagesize=A4)
    width, height = A4

    # Set initial y-position for the content
    y_position = height - 100

    # Add logo and header
    c.drawImage('./static/logo.jpg', (width - 200) / 2, y_position, width=200, height=50, preserveAspectRatio=True, mask='auto')
    y_position -= 70  # Adjust y_position after logo
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_position, "SEO Analysis Report")
    y_position -= 30  # Adjust y_position after title

    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_position, f"For: {seo_data['URL']}")
    y_position -= 20  # Adjust y_position after URL
    c.drawString(30, y_position, f"Report Date: {datetime.now().strftime('%d/%m/%Y')}")
    y_position -= 40  # Space before sections

    # Technical SEO Analysis section
    if "Technical SEO" in categories:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, "Technical SEO Analysis:")
        y_position -= 20  # Adjust y_position for content
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Page Load Time: {seo_data.get('Page Load Time', 'Not available')}")
        y_position -= 20  # Adjust y_position for next item
        c.drawString(50, y_position, f"Rating: {seo_data.get('Load Time Rating', 'Not rated')}")
        y_position -= 30  # Space before next section

    # On-Page SEO Analysis section
    if "On-Page SEO" in categories:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, "On-Page SEO Analysis:")
        y_position -= 20  # Adjust y_position for content
        c.setFont("Helvetica", 12)
        title_tag = seo_data.get('Title Tag', 'No Title Found')
        wrapped_text = simpleSplit(title_tag, "Helvetica", 12, 500)  # Wraps text to fit 500 pixels width
        for line in wrapped_text:
            c.drawString(50, y_position, line)
            y_position -= 14  # Move down for the next line
        c.drawString(50, y_position, f"Title Length Status: {seo_data.get('Title Length Status', 'Not checked')}")
        y_position -= 30  # Space before next section if any

    c.save()
    return full_path

    # Add logo
    logo_path = './static/logo.jpg'
    c.drawImage(logo_path, (width - 200) / 2, height - 80, width=200, height=50, preserveAspectRatio=True, mask='auto')
    
    # Add header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, "SEO Analysis Report")

    # Add 'For:' and website URL
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 120, f"For: {seo_data['URL']}")

    # Add current date in dd/mm/yyyy format
    current_date = datetime.now().strftime('%d/%m/%Y')
    c.drawString(30, height - 140, f"Report Date: {current_date}")

    # Technical SEO Analysis section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 170, "Technical SEO Analysis:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 190, f"Page Load Time: {seo_data.get('Page Load Time', 'Not available')}")

    # Separate column for rating, in italics
    c.setFont("Helvetica-Oblique", 12)  # Italic font for rating
    c.drawString(250, height - 190, f"Rating: {seo_data.get('Load Time Rating', 'Not rated')}")

    c.save()  # Save the document
    return full_path


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
