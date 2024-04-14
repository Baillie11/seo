from flask import Flask, render_template, request, send_from_directory
from bs4 import BeautifulSoup
import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import re


app = Flask(__name__)

# Function to perform SEO analysis (simplified for this example)
def perform_seo_analysis(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'Missing'
        return {'URL': url, 'Title': title}
    except Exception as e:
        return {'URL': url, 'Error': str(e)}

# Function to create a PDF report with logo and formatted title
def create_pdf_report(seo_data, filename=None):
    # If filename is not provided, generate one dynamically
    if not filename:
        # Sanitize the URL to create a valid filename
        website_name = re.sub(r'\W+', '', seo_data['URL'])  # Remove non-alphanumeric characters
        # Get current date and time for the filename
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f'SEO_Report_{website_name}_{current_time}.pdf'

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter  # Unpack page dimensions

    # Load and insert logo
    # Define the absolute path to the logo
    current_directory = os.path.dirname(__file__)  # Get the directory where the script runs
    logo_path = os.path.join(current_directory, 'static', 'logo.png')  # Build the path to the logo file
    c.drawImage(logo_path, 30, height - 90, width=120, height=60, preserveAspectRatio=True, mask='auto')

    # Insert title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkblue)
    c.drawString(160, height - 70, "Click Ecommerce SEO Analysis")

    # Insert other data
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    text_y_position = height - 130
    c.drawString(100, text_y_position, f"SEO Report for: {seo_data['URL']}")
    text_y_position -= 20
    c.drawString(100, text_y_position, f"Title: {seo_data.get('Title', 'No Title Found')}")

    c.save()
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        seo_data = perform_seo_analysis(url)
        pdf_filename = create_pdf_report(seo_data)
        return render_template('report.html', seo_data=seo_data, pdf_filename=pdf_filename)
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
