from flask import jsonify
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
    response = {
        "success": success,
        "message": message,
        "data": _serialize_value(data),
        "errors": _serialize_value(errors),
        "timestamp": int(time.time())
    }

    return jsonify(response), status_code