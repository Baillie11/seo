"""
Main Blueprint Package
Handles core SEO analysis functionality.
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes 