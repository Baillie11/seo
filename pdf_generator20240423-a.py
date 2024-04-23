from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import os
from datetime import datetime


def create_pdf_report(seo_data, categories, filename=None):
    reports_folder = 'Reports'
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

    # Additional PDF generation code as needed

    c.save()
    return full_path
