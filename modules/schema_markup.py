"""
Schema Markup Analysis Module
Handles analysis of structured data implementation.
"""

import json
from bs4 import BeautifulSoup

def analyze_schema_implementation(soup):
    """Analyze schema markup implementation."""
    # Look for JSON-LD schema
    schema_scripts = soup.find_all('script', type='application/ld+json')
    
    # Look for Microdata schema
    microdata_elements = soup.find_all(attrs={"itemtype": True})
    
    # Look for RDFa schema
    rdfa_elements = soup.find_all(attrs={"typeof": True})
    
    schemas_found = []
    invalid_schemas = []
    
    # Analyze JSON-LD schemas
    for script in schema_scripts:
        try:
            schema_data = json.loads(script.string)
            if isinstance(schema_data, dict):
                schema_type = schema_data.get('@type', 'Unknown')
                schemas_found.append(('JSON-LD', schema_type))
            elif isinstance(schema_data, list):
                for item in schema_data:
                    if isinstance(item, dict):
                        schema_type = item.get('@type', 'Unknown')
                        schemas_found.append(('JSON-LD', schema_type))
        except json.JSONDecodeError:
            invalid_schemas.append('JSON-LD')
    
    # Analyze Microdata schemas
    for element in microdata_elements:
        schema_type = element.get('itemtype', '').split('/')[-1]
        if schema_type:
            schemas_found.append(('Microdata', schema_type))
    
    # Analyze RDFa schemas
    for element in rdfa_elements:
        schema_type = element.get('typeof', '')
        if schema_type:
            schemas_found.append(('RDFa', schema_type))
    
    # Determine status and message
    if not schemas_found and not invalid_schemas:
        return {
            'status': "bad",
            'message': "No schema markup found",
            'details': []
        }
    elif invalid_schemas:
        return {
            'status': "warning",
            'message': "Found invalid schema markup",
            'details': {
                'valid_schemas': schemas_found,
                'invalid_schemas': invalid_schemas
            }
        }
    else:
        return {
            'status': "good",
            'message': "Valid schema markup found",
            'details': schemas_found
        }

def analyze(response, soup):
    """Analyze schema markup aspects."""
    implementation_analysis = analyze_schema_implementation(soup)
    
    return {
        'Implementation': {
            'Status': implementation_analysis['status'],
            'Details': implementation_analysis['message'],
            'Found Schemas': implementation_analysis['details']
        }
    } 