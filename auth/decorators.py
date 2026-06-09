from functools import wraps
from users.models import User
from auth.models import Role,Permission,roles_permissions
from utils.api_response import api_response
from flask_jwt_extended import get_jwt_identity,get_jwt
from sqlalchemy import and_

from functools import wraps
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_

from users.models import User
from utils.api_response import api_response


def permissions_required(permissions: list[str]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            user_id = int(get_jwt_identity())

            user = User.query.filter(
                and_(
                    User.id == user_id,
                    User.is_active == True
                )
            ).first()

            if not user:
                return api_response(
                    success=False,
                    message="User not found or not active",
                    status_code=404
                )

            if not user.role:
                return api_response(
                    success=False,
                    message="User has no role assigned",
                    status_code=403
                )

            user_permissions = {
                permission.name
                for permission in user.role.permissions
            }

            required_permissions = set(permissions)

            missing_permissions = required_permissions - user_permissions

            if missing_permissions:
                return api_response(
                    success=False,
                    message="Forbidden",
                    data={
                        "missing_permissions": list(missing_permissions)
                    },
                    status_code=403
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator