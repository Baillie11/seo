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
from pdf_generator import create_pdf_report  # Import the function from the new module
from seo_analysis import perform_seo_analysis  # Import the SEO analysis function


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        selected_categories = request.form.getlist('categories')
        print(f"URL: {url}, Categories: {selected_categories}")  # Debugging print statement
        seo_data = perform_seo_analysis(url, selected_categories)
        print(f"SEO Data: {seo_data}")  # Debugging print statement
        pdf_filename = create_pdf_report(seo_data, selected_categories)
        print(f"PDF Filename: {pdf_filename}")  # Debugging print statement
        return render_template('report.html', seo_data=seo_data, pdf_filename=pdf_filename, categories=selected_categories)
    return render_template('index.html')


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)