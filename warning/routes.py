from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from users.models import User
from utils.api_response import api_response
from warning.services import (
    delete_warning,
    get_warning,
    get_warnings,
    update_warning,
)

warning_bp = Blueprint("warnings", __name__)


def _current_user():
    user_id = int(get_jwt_identity())
    return User.query.filter_by(id=user_id).first()


@warning_bp.route("/", methods=["GET"])
@jwt_required(locations=["headers"])
def list_warnings():
    try:
        user = _current_user()
        if not user:
            return api_response(success=False, message="User not found", status_code=404)

        only_mine = request.args.get("mine", "false").lower() == "true"
        can_view_any = user.role and any(
            permission.name == "warning:view:any"
            for permission in user.role.permissions
        )
        warnings = get_warnings(user_id=user.id if only_mine or not can_view_any else None)
        return api_response(
            success=True,
            message="Warnings fetched successfully",
            data=warnings,
            status_code=200,
        )
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)


@warning_bp.route("/<int:warning_id>", methods=["GET"])
@jwt_required(locations=["headers"])
def get_warning_details(warning_id):
    try:
        user = _current_user()
        if not user:
            return api_response(success=False, message="User not found", status_code=404)
        warning = get_warning(warning_id=warning_id, user=user)
        return api_response(
            success=True,
            message="Warning fetched successfully",
            data=warning,
            status_code=200,
        )
    except PermissionError as e:
        return api_response(success=False, message=str(e), status_code=403)
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=404)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)


@warning_bp.route("/<int:warning_id>", methods=["PUT", "PATCH"])
@jwt_required(locations=["headers"])
def update_warning_details(warning_id):
    try:
        user = _current_user()
        if not user:
            return api_response(success=False, message="User not found", status_code=404)
        data = request.get_json() or {}
        warning = update_warning(warning_id=warning_id, data=data, user=user)
        return api_response(
            success=True,
            message="Warning updated successfully",
            data=warning,
            status_code=200,
        )
    except PermissionError as e:
        return api_response(success=False, message=str(e), status_code=403)
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=404)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)


@warning_bp.route("/<int:warning_id>", methods=["DELETE"])
@jwt_required(locations=["headers"])
def delete_warning_details(warning_id):
    try:
        user = _current_user()
        if not user:
            return api_response(success=False, message="User not found", status_code=404)
        delete_warning(warning_id=warning_id, user=user)
        return api_response(
            success=True,
            message="Warning deleted successfully",
            status_code=200,
        )
    except PermissionError as e:
        return api_response(success=False, message=str(e), status_code=403)
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=404)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)
