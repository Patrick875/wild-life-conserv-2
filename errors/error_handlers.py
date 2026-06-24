from werkzeug.exceptions import HTTPException
from utils.api_response import api_response
from marshmallow import ValidationError
from flask_limiter.errors import RateLimitExceeded

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return api_response(
            status_code=e.code,
            success=False,
            message=e.description,
            errors=[e.description]
        )
    @app.errorhandler(ValidationError)
    def handle_validation_errors(e):
        return api_response(
            success=False,
            status_code=400,
            message="Validation error",
            errors=[e.messages]
        )
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_error(e):
        return api_response(
            success=False,
            message='Too many requests. Please try again later.',
            status_code=429,
        )
    @app.errorhandler(Exception)
    def handle_general_exceptions(e):
        print(f"{str(e)}")
        return api_response(
            success=False,
            message='Internal server error',
            status_code=500,
            
        )
