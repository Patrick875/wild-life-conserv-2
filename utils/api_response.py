from flask import current_app, jsonify
import time


def _serialize_value(value):
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


def api_response(
    success: bool,
    message: str,
    data=None,
    errors=None,
    status_code: int = 200
):
    if status_code >= 500:
        current_app.logger.error(
            "Server error response: %s | details: %s",
            message,
            errors,
            exc_info=True,
        )
        message = "An unexpected server error occurred"
        errors = None

    response={
        "success": success,
        "message": message,
        "timestamp": int(time.time())
    }
    if data is not None:
        response["data"]=data
    if errors is not None:
        response["errors"]=errors

    return jsonify(response), status_code
