from flask import jsonify
import time


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
        "data": data,
        "errors": errors,
        "timestamp": int(time.time())
    }

    return jsonify(response), status_code