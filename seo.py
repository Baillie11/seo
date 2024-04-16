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
def create_pdf_report(seo_data, filename='SEO_Report.pdf'):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4  # Dimensions of A4 paper

    # Styles for paragraphs
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    body_style = styles['BodyText']

    # Logo
    logo_path = './static/logo.png'
    c.drawImage(logo_path, 30, height - 90, width=120, height=60, preserveAspectRatio=True, mask='auto')

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkblue)
    c.drawString(160, height - 70, "Click Ecommerce SEO Analysis")

    # SEO Report Title
    report_title = f"SEO Report for: {seo_data['URL']}"
    title_para = Paragraph(report_title, title_style)
    title_para.wrapOn(c, width - 80, height)  # Set width of the paragraph
    title_para.drawOn(c, 40, height - 150)  # Draw paragraph on canvas

    # Long Title Description
    long_title = seo_data.get('Title', 'No Title Found')
    long_title_para = Paragraph(long_title, body_style)
    long_title_para.wrapOn(c, width - 80, height)  # Wrap and set width
    long_title_para.drawOn(c, 40, height - 180)  # Adjust position as needed

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
