from extensions import db 
from database.baseModel import BaseModel


class MediaFile(BaseModel):

    __tablename__ = "media_files"
    
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))  
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    file_path = db.Column(db.String(500))  
    
    question_name = db.Column(db.String(255))  
    upload_status = db.Column(db.String(50), default="pending") 
    
    submission = db.relationship("FormSubmission", back_populates="media_files")
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'question_name': self.question_name,
            'upload_status': self.upload_status,
            'created_at': self.created_at
        }