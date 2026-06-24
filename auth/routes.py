from flask import Blueprint, request
from marshmallow import ValidationError

from auth.schemas import LoginSchema,SignupSchema,ForgotPasswordSchema,PasswordResetSchema,PasswordResetVerifySchema
from auth.services import login as login_user,signup_user,forgot_password_init,password_reset_verify,password_reset
from utils.api_response import api_response

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login
    ---
    description: login into the app
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/UserLogin'
    responses:
      200:
        description: User logged in successfuly
      400:
        description: Bad request
      500:
        description: Internal server error

    """
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
    """
    Signup
    ---
    description: login into the app
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/UserSignup'
    responses:
      200:
        description: Account created successfuly, proceed to login
      400:
        description: Bad request
      500:
        description: Internal server error
    """
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

@auth_bp.route("/password-reset/request",methods=["POST"])
def forgot_password():
    """
    Forgot Password
    ---
    description: Request a password reset
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
              description: The email address of the user requesting a password reset.
          required:
            - email
    responses:
      200:
        description: Password reset request successful, check your email for further instructions.
      400:
        description: Bad request, invalid input data.
      500:
        description: Internal server error.
    """
    try:
        form_data=ForgotPasswordSchema().load(request.json)
        result=forgot_password_init(form_data)
        return api_response(
        success=True,
        message="Password reset request successful, check your email for further instructions.",
        status_code=200,
    )
    except ValidationError as error:
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )       
    
@auth_bp.route("/password-reset/verify",methods=["POST"])
def password_reset_verify_route():
    """
    Verify Password Reset OTP
    ---
    description: Verify the OTP sent to the user's email for password reset.
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/PasswordResetVerify'
    responses:
      200:
        description: OTP verified successfully, proceed to reset your password.
      400:
        description: Bad request, invalid input data or OTP verification failed.
      500:
        description: Internal server error.
    """
    try:
        form_data=PasswordResetVerifySchema().load(request.json)
        result=password_reset_verify(form_data)
        return api_response(
            success=True,
            message="OTP verified successfully, proceed to reset your password.",
            status_code=200,
        )
    except ValidationError as error:
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )

@auth_bp.route("/password-reset",methods=["POST"])
def password_reset_route():
    """
    Reset Password
    ---
    description: Reset the user's password using a valid reset token.
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/PasswordReset'
    responses:
      200:  
        description: Password reset successful, you can now log in with your new password.
      400:
        description: Bad request, invalid input data or reset token verification failed.
      500:
        description: Internal server error.
    """
    try:
        form_data=PasswordResetSchema().load(request.json)
        result=password_reset(form_data)
        return api_response(
            success=True,
            message="Password reset successful, you can now log in with your new password.",
            status_code=200,
        )
    except ValidationError as error:
        return api_response(
            success=False,
            message="Validation failed",
            errors=error.messages,
            status_code=400
        )
    