"""
Authentication Package
Handles user authentication and registration.
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes 