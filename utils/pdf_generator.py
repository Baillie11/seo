"""
PDF Report Generator
Creates PDF reports from SEO analysis results.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from datetime import datetime
import re
import os

# Import the metrics guide from our Python module
from utils.metrics_data import metrics_guide

def clean_url_for_filename(url):
    """Clean URL to create a valid filename."""
    # Remove protocol (http:// or https://)
    url = re.sub(r'^https?://', '', url)
    # Remove www.
    url = re.sub(r'^www\.', '', url)
    # Remove trailing slash
    url = url.rstrip('/')
    # Replace invalid filename characters
    url = re.sub(r'[<>:"/\\|?*]', '_', url)
    # Add timestamp to avoid overwriting if multiple reports for same site
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"seo_report_for_{url}_{timestamp}.pdf"

def add_metrics_guide(content, styles):
    """Add the metrics guide section to the report."""
    # Add a page break before the metrics guide
    content.append(PageBreak())
    
    # Add Metrics Guide header
    guide_header_style = ParagraphStyle(
        'GuideHeader',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    content.append(Paragraph("SEO Metrics Guide", guide_header_style))
    content.append(Spacer(1, 20))
    
    # Add introduction
    intro_text = """This guide explains the SEO metrics used in this report. Each metric includes a description, 
    what constitutes good and bad values, and why it matters for your website's SEO performance."""
    content.append(Paragraph(intro_text, styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Create styles for the guide
    category_style = ParagraphStyle(
        'CategoryHeader',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2c3e50')
    )
    
    metric_style = ParagraphStyle(
        'MetricHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=5,
        textColor=colors.HexColor('#34495e')
    )
    
    # Add each category and its metrics
    for category, metrics in metrics_guide.items():
        content.append(Paragraph(category, category_style))
        
        for metric, info in metrics.items():
            # Add metric name
            content.append(Paragraph(metric, metric_style))
            
            # Create table data for metric information
            table_data = [
                ['Description:', info['description']],
                ['Good Value:', info['good']],
            ]
            
            # Add warning value if present
            if 'warning' in info:
                table_data.append(['Warning Value:', info['warning']])
                
            table_data.append(['Poor Value:', info['bad']])
            table_data.append(['Why it Matters:', info['why']])
            
            # Create and style the table
            table = Table(table_data, colWidths=[1.5*inch, 5*inch])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            content.append(table)
            content.append(Spacer(1, 10))

def create_report(seo_data, categories):
    """Create a PDF report from SEO analysis data."""
    # Create a clean filename from the URL
    filename = clean_url_for_filename(seo_data['URL'])
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create full file path
    filepath = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50')
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeader',
        parent=styles['Heading3'],
        spaceAfter=6,
        textColor=colors.HexColor('#34495e')
    ))

    styles.add(ParagraphStyle(
        name='SiteURL',
        parent=styles['Heading2'],
        textColor=colors.HexColor('#0d6efd'),
        fontSize=14,
        spaceAfter=20,
        alignment=0  # Left alignment (0=left, 1=center, 2=right)
    ))
    
    # Build the document content
    content = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        alignment=0  # Left alignment
    )
    content.append(Paragraph("SEO Analysis Report", title_style))
    content.append(Spacer(1, 6))
    
    # Add site URL with left alignment
    content.append(Paragraph(f"for {seo_data['URL']}", styles['SiteURL']))
    content.append(Spacer(1, 12))
    
    # Add report info
    report_info = [
        ['Analysis Date:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
    ]
    
    info_table = Table(report_info, colWidths=[1.5*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Ensure left alignment
    ]))
    content.append(info_table)
    content.append(Spacer(1, 20))
    
    # Add basic analysis results
    for category in categories:
        if category in seo_data:
            content.append(Paragraph(category, styles['SectionHeader']))
            
            # Convert the data to a table format
            table_data = []
            for key, value in seo_data[category].items():
                if isinstance(value, dict):
                    # Handle nested dictionaries
                    content.append(Paragraph(key, styles['SubHeader']))
                    sub_table_data = [[k, str(v)] for k, v in value.items()]
                    table = Table(sub_table_data, colWidths=[2.5*inch, 4*inch])
                    table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
                    ]))
                    content.append(table)
                else:
                    table_data.append([key, str(value)])
            
            if table_data:
                table = Table(table_data, colWidths=[2.5*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(table)
            
            content.append(Spacer(1, 15))
    
    # Add enhanced analysis results if available
    if 'enhanced_results' in seo_data:
        content.append(Paragraph("Enhanced Analysis Results", styles['SectionHeader']))
        enhanced_results = seo_data['enhanced_results']
        
        # Competitor Analysis
        if enhanced_results.get('competitor_analysis'):
            content.append(Paragraph("Competitor Analysis", styles['SubHeader']))
            comp_data = enhanced_results['competitor_analysis']['summary']
            table_data = [
                ['Metric', 'Your Website', 'Competitor Average'],
                ['Word Count', str(comp_data['word_count']['main']), 
                 f"{comp_data['word_count']['avg_competitors']:.2f}"],
                ['Load Time', str(comp_data['load_time']['main']), 
                 f"{comp_data['load_time']['avg_competitors']:.2f}s"]
            ]
            table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(table)
            content.append(Spacer(1, 15))
        
        # Keyword Analysis
        if enhanced_results.get('keyword_suggestions'):
            content.append(Paragraph("Keyword Analysis", styles['SubHeader']))
            kw_data = enhanced_results['keyword_suggestions']
            
            # Current keywords density
            content.append(Paragraph("Current Keyword Density", styles['Normal']))
            table_data = [['Keyword', 'Density']]
            for kw, density in kw_data['current_keywords']['keyword_density'].items():
                table_data.append([kw, f"{density:.2f}%"])
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(table)
            
            # Suggested keywords
            content.append(Paragraph("Suggested Keywords", styles['Normal']))
            content.append(Paragraph(", ".join(kw_data['suggested_keywords']), 
                                  ParagraphStyle('Keywords', 
                                               parent=styles['Normal'],
                                               textColor=colors.HexColor('#0d6efd'))))
            content.append(Spacer(1, 15))
        
        # Mobile Analysis
        if enhanced_results.get('mobile_analysis'):
            content.append(Paragraph("Mobile Friendliness", styles['SubHeader']))
            mobile_data = enhanced_results['mobile_analysis']
            content.append(Paragraph(f"Mobile Score: {mobile_data['mobile_score']}/100", 
                                  ParagraphStyle('Score', 
                                               parent=styles['Normal'],
                                               fontSize=12,
                                               textColor=colors.HexColor('#28a745' if mobile_data['mobile_score'] >= 80 else '#dc3545'))))
            
            for check_name, check in mobile_data['checks'].items():
                content.append(Paragraph(f"• {check_name.replace('_', ' ').title()}", 
                                      ParagraphStyle('CheckName',
                                                   parent=styles['Normal'],
                                                   fontName='Helvetica-Bold')))
                content.append(Paragraph(check['message'], styles['Normal']))
                if check.get('recommendation'):
                    content.append(Paragraph(f"Recommendation: {check['recommendation']}", 
                                          ParagraphStyle('Recommendation', 
                                                       parent=styles['Normal'],
                                                       leftIndent=20,
                                                       textColor=colors.HexColor('#0d6efd'))))
            content.append(Spacer(1, 15))
        
        # Speed Insights
        if enhanced_results.get('speed_insights'):
            content.append(Paragraph("Speed Insights", styles['SubHeader']))
            speed_data = enhanced_results['speed_insights']
            
            content.append(Paragraph(f"Performance Score: {speed_data['performance_score']}/100",
                                  ParagraphStyle('Score',
                                               parent=styles['Normal'],
                                               fontSize=12,
                                               textColor=colors.HexColor('#28a745' if speed_data['performance_score'] >= 80 else '#dc3545'))))
            content.append(Paragraph(f"Load Time: {speed_data['load_time']}s", styles['Normal']))
            
            # Resource breakdown
            content.append(Paragraph("Resource Breakdown", styles['Normal']))
            table_data = [['Resource Type', 'Size (MB)']]
            for res_type, size in speed_data['page_size']['breakdown'].items():
                table_data.append([res_type.title(), f"{size/1024:.2f}"])
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(table)
            
            # Recommendations
            content.append(Paragraph("Recommendations", styles['Normal']))
            for rec in speed_data['recommendations']:
                content.append(Paragraph(f"• {rec['message']}", 
                                      ParagraphStyle('RecommendationTitle',
                                                   parent=styles['Normal'],
                                                   fontName='Helvetica-Bold')))
                content.append(Paragraph(rec['recommendation'], 
                                      ParagraphStyle('Recommendation', 
                                                   parent=styles['Normal'],
                                                   leftIndent=20,
                                                   textColor=colors.HexColor('#0d6efd'))))
            content.append(Spacer(1, 15))
    
    # Add the metrics guide at the end
    add_metrics_guide(content, styles)
    
    # Build the PDF
    doc.build(content)
    return filename 