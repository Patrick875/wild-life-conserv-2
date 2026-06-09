from database.baseModel import BaseModel
from extensions import db

class WarningFeedback(BaseModel):
    __tablename__ = "warning_feedbacks"

    warning_id = db.Column(
        db.Integer(),
        db.ForeignKey("warnings.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(db.String)

    warning = db.relationship(
        "Warning",
        back_populates="feedbacks"
    )

    user = db.relationship(
        "User",
        back_populates="warning_feedbacks"
    )

    def to_dict(self, include_user=True, include_warning=False):
        data = {
            "id": self.id,
            "warning_id": self.warning_id,
            "message": self.message,
            "user_id": self.user_id,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

        if include_user:
            data["user"] = self.user.to_dict() if self.user else None

        if include_warning:
            data["warning"] = self.warning.to_dict(include_feedbacks=False) if self.warning else None

        return data