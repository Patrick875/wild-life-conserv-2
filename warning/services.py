from sqlalchemy.orm import joinedload

from extensions import db
from warning.models import Warning
from warning_feedbacks.models import WarningFeedback


def _user_has_permission(user, permission):
    return bool(
        user
        and user.role
        and any(item.name == permission for item in user.role.permissions)
    )


def get_warnings(user_id=None, include_feedbacks=True):
    query = Warning.query.order_by(Warning.created_at.desc())
    if user_id:
        query = query.filter(Warning.user_id == user_id)

    warnings = query.options(joinedload(Warning.feedbacks)).all()
    return [
        warning.to_dict(include_feedbacks=include_feedbacks)
        for warning in warnings
    ]


def get_warning(warning_id, user=None, include_feedbacks=True):
    warning = Warning.query.filter_by(id=warning_id).first()
    if not warning:
        raise ValueError("Warning not found")

    if user and warning.user_id != user.id and not _user_has_permission(user, "warning:view:any"):
        raise PermissionError("Unauthorized to access this warning")

    return warning.to_dict(include_feedbacks=include_feedbacks)


def update_warning(warning_id, data, user):
    warning = Warning.query.filter_by(id=warning_id).first()
    if not warning:
        raise ValueError("Warning not found")

    can_update_any = _user_has_permission(user, "warning:update:any")
    can_update_own = _user_has_permission(user, "warning:update:own")
    if not can_update_any and (warning.user_id != user.id or not can_update_own):
        raise PermissionError("Unauthorized to update this warning")

    if "submission_data" in data:
        warning.submission_data = data["submission_data"]
    if "status" in data and data["status"]:
        warning.status = data["status"]
    if "kobo_submission_id" in data:
        warning.kobo_submission_id = data["kobo_submission_id"]

    db.session.commit()
    return warning.to_dict(include_feedbacks=True)


def delete_warning(warning_id, user):
    warning = Warning.query.filter_by(id=warning_id).first()
    if not warning:
        raise ValueError("Warning not found")

    can_delete_any = _user_has_permission(user, "warning:delete:any")
    if warning.user_id != user.id and not can_delete_any:
        raise PermissionError("Unauthorized to delete this warning")

    WarningFeedback.query.filter_by(warning_id=warning.id).delete()
    db.session.delete(warning)
    db.session.commit()
    return True
