from warning_feedbacks.models import WarningFeedback
from warning.models import Warning
from extensions import db
from sqlalchemy.orm import joinedload
from extensions import pusher_client
from users.models import User
from notificaitions.services import (
    build_feedback_notification_payload,
    publish_beams_to_users,
)


def _user_has_permission(user, permission):
    return bool(
        user
        and user.role
        and any(item.name == permission for item in user.role.permissions)
    )


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
        payload = build_feedback_notification_payload(warning, feedback, user)

        if user_id != warning.user_id and pusher_client:
             pusher_client.trigger(
                  channels=[f"private-user-{post_owner_id}"],
                  event_name="warning.feedback.created",
                  data=payload
             )

        # if user_id != warning.user_id:
        #      try:
        #           publish_beams_to_users([post_owner_id], payload)
        #      except ValueError:
        #           pass
        
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


def update_feedback(user_id: int, feedback_id: int, data: dict):
    feedback = WarningFeedback.query.filter_by(id=feedback_id).first()
    user = User.query.filter_by(id=user_id).first()

    if not feedback:
        raise ValueError("Feedback not found")
    if not user:
        raise ValueError("User not found")

    can_update_any = _user_has_permission(user, "warning_feedback:update:any")
    if feedback.user_id != user_id and not can_update_any:
        raise PermissionError("Unauthorized to update this feedback")

    message = data.get("message")
    if message is not None:
        if len(message.strip()) < 3:
            raise ValueError("Message must be at least 3 characters")
        feedback.message = message

    db.session.commit()
    return feedback.to_dict(include_user=True)


def delete_feedback(user_id: int, feedback_id: int):
    feedback = WarningFeedback.query.filter_by(id=feedback_id).first()
    user = User.query.filter_by(id=user_id).first()

    if not feedback:
        raise ValueError("Feedback not found")
    if not user:
        raise ValueError("User not found")

    can_delete_any = _user_has_permission(user, "warning_feedback:delete:any")
    if feedback.user_id != user_id and not can_delete_any:
        raise PermissionError("Unauthorized to delete this feedback")

    warning = Warning.query.filter_by(id=feedback.warning_id).first()
    if warning and warning.feedback_count and warning.feedback_count > 0:
        warning.feedback_count -= 1

    db.session.delete(feedback)
    db.session.commit()
    return True
