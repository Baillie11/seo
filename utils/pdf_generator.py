"""
PDF Report Generator
Handles the generation of PDF reports from SEO analysis data.
"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_report(seo_data, categories, filename=None):
    """Generate a PDF report from the SEO analysis data."""
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