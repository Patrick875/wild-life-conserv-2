from flask import Blueprint, request
from marshmallow import ValidationError

from auth.schemas import LoginSchema,SignupSchema
from auth.services import login as login_user,signup_user
from utils.api_response import api_response

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = LoginSchema().load(request.get_json())

        result = login_user(data)

        return api_response(
            success=True,
            message="Logged in successfully",
            data=result,
            status_code=200
        )

    except ValidationError as error:
        print(error.messages)
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )

    except ValueError as error:
        print(str(error))
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

@auth_bp.route("/register", methods=["POST"])
def signup():
    try:
        form_data=SignupSchema().load(request.json)
        result=signup_user(form_data)
        print(result)
        return api_response(
            success=True,
            message="Account created successfuly, proceed to login",
            status_code=200,
        )
    
    except ValidationError as error:
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )
    except ValueError as err:
        return api_response(
            success=False,
            message="Something wrong happened",
            errors=str(err),
            status_code=400
        )

