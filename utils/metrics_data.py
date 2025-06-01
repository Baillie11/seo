"""
Metrics Guide Data
Contains the definitions and explanations for all SEO metrics used in the reports.
"""

metrics_guide = {
    "Technical SEO": {
        "Load Time": {
            "description": "The time it takes for your page to fully load.",
            "good": "Under 3 seconds",
            "warning": "3-5 seconds",
            "bad": "Over 5 seconds",
            "why": "Faster loading times improve user experience and SEO rankings."
        },
        "Mobile Friendly": {
            "description": "Whether your site works well on mobile devices.",
            "good": "Yes",
            "bad": "No",
            "why": "Most web traffic comes from mobile devices. Google prioritizes mobile-friendly sites."
        },
        "SSL Certificate": {
            "description": "Security certificate that enables HTTPS.",
            "good": "Valid SSL certificate",
            "bad": "No SSL or expired",
            "why": "HTTPS is required for security and is a ranking factor for Google."
        },
        "Robots.txt": {
            "description": "File that guides search engine crawlers.",
            "good": "Present and properly configured",
            "warning": "Present but needs optimization",
            "bad": "Missing or blocking important content",
            "why": "Helps search engines understand which pages to index.",
            "creation_info": "If missing, we can help create a robots.txt file with recommended settings.",
            "auto_creation": "The tool can attempt to create a robots.txt file automatically, or provide you with the content to create it manually."
        },
        "Sitemap.xml": {
            "description": "XML file listing all important pages on your site.",
            "good": "Present and valid XML format",
            "warning": "Present but invalid format",
            "bad": "Missing",
            "why": "Helps search engines discover and index all your pages efficiently.",
            "creation_info": "If missing, we can generate a sitemap.xml based on your site's structure.",
            "auto_creation": "The tool can attempt to create a sitemap.xml file automatically, or provide you with the content to create it manually."
        }
    },
    "On-Page SEO": {
        "Title Tag": {
            "description": "The main title of your webpage.",
            "good": "50-60 characters, includes main keyword",
            "warning": "Too long/short or missing keyword",
            "bad": "Missing or duplicate",
            "why": "One of the most important SEO elements for ranking."
        },
        "Meta Description": {
            "description": "Summary of your page content.",
            "good": "150-160 characters, compelling description with keywords",
            "warning": "Too long/short or missing keywords",
            "bad": "Missing or duplicate",
            "why": "Affects click-through rates from search results."
        },
        "Header Tags": {
            "description": "Hierarchical structure of page headings (H1-H6).",
            "good": "Proper hierarchy, includes keywords",
            "warning": "Improper structure",
            "bad": "Missing or multiple H1s",
            "why": "Helps search engines understand content structure."
        }
    },
    "Content SEO": {
        "Word Count": {
            "description": "Total number of words on the page.",
            "good": "Over 1000 words for main content",
            "warning": "300-1000 words",
            "bad": "Under 300 words",
            "why": "Longer, quality content tends to rank better."
        },
        "Keyword Density": {
            "description": "Frequency of keyword usage in content.",
            "good": "1-3%",
            "warning": "3-5%",
            "bad": "Over 5% (keyword stuffing)",
            "why": "Natural keyword usage helps rankings without being spammy."
        },
        "Content Quality": {
            "description": "Overall content value and readability.",
            "good": "Original, well-structured, error-free",
            "warning": "Some issues with structure/errors",
            "bad": "Duplicate/thin content, many errors",
            "why": "High-quality content is essential for rankings and user engagement."
        }
    },
    "User Experience": {
        "Mobile Viewport": {
            "description": "How well content adapts to different screen sizes.",
            "good": "Properly configured viewport",
            "bad": "No viewport or improper configuration",
            "why": "Essential for mobile usability and rankings."
        },
        "Font Size": {
            "description": "Text readability on different devices.",
            "good": "16px or larger for body text",
            "warning": "12-15px",
            "bad": "Under 12px",
            "why": "Readable text improves user experience and reduces bounce rates."
        },
        "Tap Targets": {
            "description": "Size and spacing of clickable elements.",
            "good": "At least 48x48px with adequate spacing",
            "warning": "Some targets too small/close",
            "bad": "Many small/crowded targets",
            "why": "Proper sizing ensures good mobile usability."
        }
    },
    "Security": {
        "HTTPS": {
            "description": "Secure connection protocol.",
            "good": "HTTPS enabled and properly configured",
            "bad": "No HTTPS or misconfigured",
            "why": "Required for security and SEO ranking."
        },
        "Mixed Content": {
            "description": "Mixing secure and insecure content.",
            "good": "No mixed content",
            "warning": "Some passive mixed content",
            "bad": "Active mixed content",
            "why": "Mixed content can cause security warnings and affect user trust."
        }
    },
    "Schema Markup": {
        "Implementation": {
            "description": "Structured data for search engines.",
            "good": "Properly implemented relevant schemas",
            "warning": "Partial implementation",
            "bad": "Missing or invalid schema",
            "why": "Helps search engines understand content and enables rich results."
        }
    },
    "Speed Insights": {
        "Performance Score": {
            "description": "Overall loading performance score.",
            "good": "90-100",
            "warning": "50-89",
            "bad": "0-49",
            "why": "Page speed is a ranking factor and affects user experience."
        },
        "First Contentful Paint": {
            "description": "Time until first content appears.",
            "good": "Under 1.8s",
            "warning": "1.8-3s",
            "bad": "Over 3s",
            "why": "Affects perceived load speed and user experience."
        }
    },
    "Ranking Analysis": {
        "Google Index Status": {
            "description": "Whether your site is indexed in Google's search results.",
            "good": "Indexed",
            "bad": "Not indexed",
            "why": "Being indexed is essential for appearing in search results."
        },
        "Domain Authority": {
            "description": "Moz's prediction of how well a website will rank on search engines.",
            "good": "Above 50",
            "warning": "20-50",
            "bad": "Below 20",
            "why": "Higher domain authority typically correlates with better search rankings."
        },
        "Page Authority": {
            "description": "Prediction of how well a specific page will rank.",
            "good": "Above 40",
            "warning": "20-40",
            "bad": "Below 20",
            "why": "Higher page authority indicates better potential for ranking in search results."
        },
        "Social Signals": {
            "description": "Presence and activity on major social media platforms.",
            "good": "Active presence on multiple platforms",
            "warning": "Limited social presence",
            "bad": "No social presence",
            "why": "Social signals can indirectly influence rankings and drive traffic."
        },
        "Traffic Estimates": {
            "description": "Estimated monthly website traffic.",
            "good": "Increasing trend",
            "warning": "Stable",
            "bad": "Decreasing trend",
            "why": "Traffic trends can indicate site health and content effectiveness."
        }
    }
} 