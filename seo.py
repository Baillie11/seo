from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from bs4 import BeautifulSoup
import requests

# Function to validate the URL
def is_valid_url(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Function to perform SEO analysis with suggestions
def perform_seo_analysis(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = {}

    # Title tag analysis
    title = soup.title.string if soup.title else None
    if title:
        results['Title Tag'] = title
        results['Title Tag Suggestion'] = "Good" if len(title) < 60 else "Consider reducing the title length to under 60 characters for optimal display."
    else:
        results['Title Tag'] = 'Missing'
        results['Title Tag Suggestion'] = "Add a title tag to improve the relevance in search engine results."

    # H1 tag analysis
    h1_tags = soup.find_all('h1')
    if h1_tags:
        results['H1 Tag'] = ', '.join([tag.text.strip() for tag in h1_tags])
        results['H1 Tag Suggestion'] = "Good" if len(h1_tags) == 1 else "Multiple H1 tags found, consider using only one H1 tag for best SEO practices."
    else:
        results['H1 Tag'] = 'Missing'
        results['H1 Tag Suggestion'] = "Add an H1 tag to enhance SEO and structure the page content better."

    # Meta description analysis
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_content = meta_description['content'] if meta_description else None
    if meta_content:
        results['Meta Description'] = meta_content
        results['Meta Description Suggestion'] = "Good" if 50 <= len(meta_content) <= 160 else "Adjust the length to between 50-160 characters for optimal effectiveness."
    else:
        results['Meta Description'] = 'Missing'
        results['Meta Description Suggestion'] = "Add a meta description to improve click-through rates from search engine results."

    return results

# Function to create a PDF report
def create_pdf_report(file_path, seo_data):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter  # Unpack page dimensions

    c.drawString(100, height - 100, "SEO Analysis Report")
    y_position = height - 140
    for key, value in seo_data.items():
        c.drawString(80, y_position, f"{key}: {value}")
        y_position -= 40
        if "Suggestion" in key:
            c.drawString(80, y_position, f"Suggestion: {value}")
            y_position -= 40

    c.save()

# Main function that runs the program
def main():
    url = input("Please enter the website URL to analyze: ")
    if is_valid_url(url):
        seo_results = perform_seo_analysis(url)
        output_file_path = 'SEO_Report.pdf'
        create_pdf_report(output_file_path, seo_results)
        print(f"PDF report generated at: {output_file_path}")
    else:
        print("Invalid URL or the website is not reachable. Please check the URL and try again.")

# Call the main function
main()
