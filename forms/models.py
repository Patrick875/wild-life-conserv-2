from extensions import db
from database.baseModel import BaseModel
from datetime import datetime
import uuid

from users.models import User


class FormTemplate(BaseModel):
    __tablename__ = "form_templates"
    
    kobo_form_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    form_structure = db.Column(db.JSON) 
    version = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    submissions = db.relationship("FormSubmission", back_populates="form_template", cascade="all, delete-orphan")


class FormSubmission(BaseModel):
    __tablename__ = "form_submissions"
    
    form_template_id = db.Column(db.Integer, db.ForeignKey('form_templates.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    submission_data = db.Column(db.JSON, nullable=False)  # Form answers
    device_id = db.Column(db.String(255))
    app_version = db.Column(db.String(50))
    
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    location_accuracy = db.Column(db.Float)
    altitude = db.Column(db.Float)
    
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When user submitted
    received_at = db.Column(db.DateTime, default=datetime.utcnow)  # When API received
    
    kobo_submission_id = db.Column(db.String(255))  
    sync_status = db.Column(db.String(50), default="pending")  
    sync_attempts = db.Column(db.Integer, default=0)
    last_sync_attempt = db.Column(db.DateTime)
    sync_error = db.Column(db.Text)
    
    form_template = db.relationship("FormTemplate", back_populates="submissions")
    user = db.relationship("User", back_populates="submissions")
    media_files = db.relationship("MediaFile", back_populates="submission", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'form_template_id': self.form_template_id,
            'user_id': self.user_id,
            'submission_data': self.submission_data,
            'device_id': self.device_id,
            'app_version': self.app_version,
            'location': {
                'latitude': self.location_latitude,
                'longitude': self.location_longitude,
                'accuracy': self.location_accuracy,
                'altitude': self.altitude
            },
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

