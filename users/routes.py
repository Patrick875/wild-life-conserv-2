from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from users.models import User
from users.services import get_all_users
from utils.api_response import api_response

users_bp=Blueprint("users",__name__)


@users_bp.route("/me", methods=["GET"])
@jwt_required(locations=["headers"])
def get_current_user():
    """Get the authenticated user's profile and assigned role.
    ---
    tags:
      - Users
    security:
      - BearerAuth: []
    responses:
      200:
        description: Current user fetched successfully.
      401:
        description: A valid bearer token was not supplied.
      404:
        description: The authenticated user no longer exists.
    """
    user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not user:
        return api_response(
            success=False,
            message="User not found",
            status_code=404,
        )

    return api_response(
        success=True,
        data=user.to_dict(),
        status_code=200,
        message="Current user fetched successfully",
    )

@users_bp.route("/",methods=["GET"])
def get_app_users():
    """List application users.
    ---
    tags:
      - Users
    responses:
      200:
        description: All application users fetched successfully.
    """
    all_users=get_all_users()
    return api_response(
        success=True,
        data=all_users,
        status_code=200,
        message='All users fetched successfuly'
    )
