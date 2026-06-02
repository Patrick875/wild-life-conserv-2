from database.baseModel import BaseModel
from extensions import db
from datetime import datetime

class SyncLog(BaseModel):
    __tablename__ = "sync_logs"
    
    operation_type = db.Column(db.String(50), nullable=False)  
    status = db.Column(db.String(50), nullable=False) 
    
    
    items_processed = db.Column(db.Integer, default=0)
    items_success = db.Column(db.Integer, default=0)
    items_failed = db.Column(db.Integer, default=0)
    error_details = db.Column(db.JSON)
    
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Float)
    
    def to_dict(self):

        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'status': self.status,
            'items_processed': self.items_processed,
            'items_success': self.items_success,
            'items_failed': self.items_failed,
            'error_details': self.error_details,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at
        }
