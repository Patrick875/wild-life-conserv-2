from extensions import db
from database.baseModel import BaseModel

class MediaFile(BaseModel):
    __tablename__ = "media_files"

    submission_id = db.Column(
        db.Integer,
        db.ForeignKey("form_submissions.id"),
        nullable=True
    )
    create_by=db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    question_name = db.Column(db.String(255))

    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))      # image, video, document
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)

    # Storage info
    provider = db.Column(db.String(50), default="local")  # local, cloudinary, minio
    public_id = db.Column(db.String(500))                 # Cloudinary public_id / MinIO key
    file_path = db.Column(db.String(500))                 # local path or storage key
    url = db.Column(db.String(1000))                      # original/public URL
    optimized_url = db.Column(db.String(1000))            # transformed URL

    # Media metadata
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration = db.Column(db.Float)
    format = db.Column(db.String(50))

    upload_status = db.Column(db.String(50), default="orphan")  # orphan, linked, deleted

    submission = db.relationship("FormSubmission", back_populates="media_files")
    user=db.relationship("User",back_populates="uploads")

    def to_dict(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "question_name": self.question_name,

            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "file_size": self.file_size,

            "provider": self.provider,
            "public_id": self.public_id,
            "file_path": self.file_path,
            "url": self.url,
            "optimized_url": self.optimized_url,

            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "format": self.format,

            "upload_status": self.upload_status,
            "created_at": self.created_at,
            "user_id":self.create_by
        }