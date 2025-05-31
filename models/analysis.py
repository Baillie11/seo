"""
Analysis Model
Stores SEO analysis results and metadata.
"""

from datetime import datetime
from . import db

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_path = db.Column(db.String(500))
    categories = db.Column(db.String(500))  # Stored as comma-separated values
    
    def __repr__(self):
        return f'<Analysis {self.url}>' 