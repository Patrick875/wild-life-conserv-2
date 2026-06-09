from database.baseModel import BaseModel
from extensions import db

class Warning(BaseModel):
    __tablename__ = "warnings"

    kobo_form_id = db.Column(db.String(255), nullable=False)
    kobo_submission_id = db.Column(db.String(255), nullable=True)
    submission_data = db.Column(db.JSON(), nullable=False)

    status = db.Column(
        db.String(),
        default="pending"
    )

    user_id = db.Column(
        db.Integer(),
        db.ForeignKey("users.id"),
        nullable=False
    )

    feedback_count = db.Column(
        db.Integer(),
        default=0
    )

    user = db.relationship(
        "User",
        back_populates="warnings"
    )

    feedbacks = db.relationship(
        "WarningFeedback",
        back_populates="warning"
    )

    def to_dict(self, include_feedbacks=False):
        data = {
            "id": self.id,
            "kobo_submission_id": self.kobo_submission_id,
            "submission_data": self.submission_data,
            "status": self.status,
            "user_id": self.user_id,
            "feedback_count": self.feedback_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if include_feedbacks:
            data["feedbacks"] = [
                f.to_dict(include_user=True, include_warning=False)
                for f in self.feedbacks
            ]

        return data

    def update_feedback_count(self):
        self.feedback_count += 1