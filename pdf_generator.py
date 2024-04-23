from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import os
from datetime import datetime
import re

def create_pdf_report(seo_data, categories, filename=None):
    reports_folder = 'Reports'
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)

    if not filename:
        clean_url = seo_data['URL'].replace('http://', '').replace('https://', '')
        sanitized_url = re.sub(r'[^\w\s-]', '', clean_url).replace(' ', '_').replace('.', '_')
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format date and time as YYYYMMDD_HHMMSS
        filename = f"SEO_Report_for-{sanitized_url}_{current_datetime}.pdf"  # Append date and time to the filename

    full_path = os.path.join(reports_folder, filename)
    c = canvas.Canvas(full_path, pagesize=A4)
    width, height = A4

    y_position = height - 100
    c.drawImage('./static/logo.jpg', (width - 200) / 2, y_position, width=200, height=50, preserveAspectRatio=True, mask='auto')
    y_position -= 70
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_position, "SEO Analysis Report")
    y_position -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_position, f"For: {seo_data['URL']}")
    y_position -= 20
    c.drawString(30, y_position, f"Report Date: {datetime.now().strftime('%d/%m/%Y')}")
    y_position -= 40

    # Technical SEO Analysis section
    if "Technical SEO" in categories:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, "Technical SEO Analysis:")
        y_position -= 20
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Page Load Time: {seo_data.get('Page Load Time', 'Not available')}")
        y_position -= 20
        c.drawString(50, y_position, f"Rating: {seo_data.get('Load Time Rating', 'Not rated')}")
        y_position -= 30

    # On-Page SEO Analysis section
    if "On-Page SEO" in categories:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, "On-Page SEO Analysis:")
        y_position -= 20
        c.setFont("Helvetica", 12)
        title_tag = seo_data.get('Title Tag', 'No Title Found')
        title_length = len(title_tag)
        wrapped_text = simpleSplit(title_tag, "Helvetica", 12, 500)  # Wraps text to fit 500 pixels width
        for line in wrapped_text:
            c.drawString(50, y_position, line)
            y_position -= 14  # Move down for the next line
        c.drawString(50, y_position, f"Title Character Count: {title_length}")  # Display the character count
        y_position -= 20
        c.drawString(50, y_position, f"Title Length Status: {seo_data.get('Title Length Status', 'Not checked')}")
        y_position -= 30  # Space before next section if any

    c.save()
    return full_path
