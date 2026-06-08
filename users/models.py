from extensions import db
from database.baseModel import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    full_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=True, index=True)
    email = db.Column(db.String, unique=False, nullable=True)
    phone_number = db.Column(db.String, unique=True, nullable=True, index=True)

    occupation = db.Column(db.String, nullable=True)
    organization = db.Column(db.String, nullable=True)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users")

    password_hash = db.Column(db.String, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String, nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

    last_login = db.Column(db.DateTime)

    submissions = db.relationship("FormSubmission", back_populates="user")
    uploads=db.relationship("MediaFile",back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "occupation": self.occupation,
            "organization": self.organization,
            "role": self.role.name if self.role else None,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }