from flask import Blueprint, request
from marshmallow import ValidationError

from auth.schemas import LoginSchema
from auth.services import login as login_user
from utils.api_response import api_response

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login_user():
    try:
        data = LoginSchema().load(request.get_json())

        token_dict = login_user(data)

        return api_response(
            success=True,
            message="Logged in successfully",
            data=token_dict,
            status_code=200
        )

    except ValidationError as error:
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )

    except ValueError as error:
        return api_response(
            success=False,
            message=str(error),
            status_code=400
        )

    except Exception as error:
        return api_response(
            success=False,
            message="An unexpected error occurred",
            errors={"details": str(error)},
            status_code=500
        )


# @auth_bp.route("/", methods=["POST"])
# def signup_user():
#     data=request.get_json()
    