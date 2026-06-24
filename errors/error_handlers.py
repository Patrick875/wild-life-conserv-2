from werkzeug.exceptions import HTTPException
from utils.api_response import api_response
from marshmallow import ValidationError

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
    @app.errorhandler(Exception)
    def handle_general_exceptions(e):
        return api_response(
            success=False,
            message='Internal server error',
            status_code=500,
            errors=[str(e)]
        )
