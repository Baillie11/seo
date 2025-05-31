"""
User Experience Analysis Module
Handles analysis of mobile viewport, font sizes, and tap targets.
"""

def analyze_viewport(soup):
    """Analyze viewport configuration."""
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport_meta:
        return {
            'status': "bad",
            'message': "No viewport configuration found"
        }
    
    content = viewport_meta.get('content', '').lower()
    if 'width=device-width' in content and 'initial-scale=1' in content:
        return {
            'status': "good",
            'message': "Properly configured viewport"
        }
    return {
        'status': "bad",
        'message': "Improper viewport configuration"
    }

def analyze_font_sizes(soup):
    """Analyze font sizes used in the content."""
    # Get all elements with font-size style or CSS classes commonly used for text
    text_elements = soup.find_all(['p', 'div', 'span', 'a', 'li'])
    font_sizes = []
    
    for elem in text_elements:
        style = elem.get('style', '')
        if 'font-size:' in style:
            size = style.split('font-size:')[1].split(';')[0].strip()
            if 'px' in size:
                font_sizes.append(int(size.replace('px', '')))
    
    if not font_sizes:
        return {
            'status': "warning",
            'message': "Could not determine font sizes"
        }
    
    min_size = min(font_sizes)
    if min_size >= 16:
        return {
            'status': "good",
            'message': f"All text is 16px or larger"
        }
    elif min_size >= 12:
        return {
            'status': "warning",
            'message': f"Some text is smaller than recommended (minimum found: {min_size}px)"
        }
    else:
        return {
            'status': "bad",
            'message': f"Text too small for mobile devices (minimum found: {min_size}px)"
        }

def analyze_tap_targets(soup):
    """Analyze tap target sizes and spacing."""
    clickable_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
    small_targets = []
    
    for elem in clickable_elements:
        style = elem.get('style', '')
        width = height = None
        
        # Check inline styles
        if 'width:' in style:
            width_str = style.split('width:')[1].split(';')[0].strip()
            if 'px' in width_str:
                width = int(width_str.replace('px', ''))
        if 'height:' in style:
            height_str = style.split('height:')[1].split(';')[0].strip()
            if 'px' in height_str:
                height = int(height_str.replace('px', ''))
        
        # If either dimension is specified and too small, add to list
        if (width and width < 48) or (height and height < 48):
            small_targets.append(elem)
    
    if not small_targets:
        return {
            'status': "good",
            'message': "All tap targets are properly sized"
        }
    elif len(small_targets) <= len(clickable_elements) * 0.2:  # 20% threshold
        return {
            'status': "warning",
            'message': f"Some tap targets ({len(small_targets)}) are too small"
        }
    else:
        return {
            'status': "bad",
            'message': f"Many tap targets ({len(small_targets)}) are too small"
        }

def analyze(response, soup, url):
    """Analyze user experience aspects."""
    viewport_analysis = analyze_viewport(soup)
    font_analysis = analyze_font_sizes(soup)
    tap_target_analysis = analyze_tap_targets(soup)
    
    return {
        'Mobile Viewport': {
            'Status': viewport_analysis['status'],
            'Details': viewport_analysis['message']
        },
        'Font Size': {
            'Status': font_analysis['status'],
            'Details': font_analysis['message']
        },
        'Tap Targets': {
            'Status': tap_target_analysis['status'],
            'Details': tap_target_analysis['message']
        }
    } 