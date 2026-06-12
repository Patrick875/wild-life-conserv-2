from warning_feedbacks.models import WarningFeedback
from warning.models import Warning
from extensions import db
from sqlalchemy.orm import joinedload
from extensions import pusher_client
from users.models import User


def add_feedback(user_id:int,data:dict):
    try:
        if not user_id:
            raise ValueError("User id is required")
        
        warning_id= data.get("warning_id")
        warning= Warning.query.filter_by(id=warning_id).first()
        user=User.query.filter_by(id=user_id).first()
        
        if not warning:
            raise ValueError("Warning not found")
        
        if not user:
            raise ValueError("User not found")
        
        feedback= WarningFeedback(
            user_id=user_id,
            **data
        )
        db.session.add(feedback)
        warning.update_feedback_count()
        db.session.commit()
        
        post_owner_id = warning.user_id
        user_data=user.to_dict()
        sender_name=user_data.get('full_name',"Someone")
        if user_id != warning.user_id:
             pusher_client.trigger(
                  channels=[f"private-user-{post_owner_id}"],
                  event_name="new-feedback",
                  data={
                       "title":"New feedback!",
                       "message":f"{sender_name} has reacted to your warning"
                  }
             )
        
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

         
    