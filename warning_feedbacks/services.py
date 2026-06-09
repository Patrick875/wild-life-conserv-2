from warning_feedbacks.models import WarningFeedback
from warning.models import Warning
from extensions import db
from sqlalchemy.orm import joinedload


def add_feedback(user_id:int,data:dict):
    try:
        if not user_id:
            raise ValueError("User id is required")
        warning_id= data.get("warning_id")
        warning= Warning.query.filter_by(id=warning_id).first()
        if not warning:
            raise ValueError("Warning not found")
        
        feedback= WarningFeedback(
            user_id=user_id,
            **data
        )
        db.session.add(feedback)
        warning.update_feedback_count()
        db.session.commit()
        
        return feedback.to_dict(include_user=True)
    except ValueError as e:
        raise ValueError(str(e))
    
def get_feedback_per_warning(warning_id:int):
    try:
        warning= Warning.query.filter_by(id=warning_id).first()
        if not warning:
                raise ValueError("Warning not found")
        
        feedbacks= WarningFeedback.query.order_by(
             WarningFeedback.created_at.desc()).options(
             joinedload(WarningFeedback.user),
             ).filter_by(warning_id=warning_id).all()

        feedbacks_normalized= [feedback.to_dict(include_user=True, include_warning=False) for feedback in feedbacks]
        return feedbacks_normalized
    except ValueError as e:
         raise ValueError(str(e))

         
    