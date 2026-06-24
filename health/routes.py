"""Operational endpoints for load balancers and deployment platforms."""

from flask import Blueprint
from sqlalchemy import text

from extensions import db
from utils.api_response import api_response


health_bp = Blueprint("health_bp", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Check whether the API process is alive.
    ---
    tags:
      - Operations
    responses:
      200:
        description: The API process is healthy. This endpoint does not check external dependencies.
    """
    return api_response(
        success=True,
        message="Service is healthy",
        data={"status": "ok"},
        status_code=200,
    )


@health_bp.route("/ready", methods=["GET"])
def readiness_check():
    """Check whether the API is ready to receive traffic.
    ---
    tags:
      - Operations
    responses:
      200:
        description: The API can reach its database and is ready to receive traffic.
      503:
        description: The database is unavailable, so the API is not ready.
    """
    try:
        db.session.execute(text("SELECT 1"))
        return api_response(
            success=True,
            message="Service is ready",
            data={"status": "ready", "database": "connected"},
            status_code=200,
        )
    except Exception:
        return api_response(
            success=False,
            message="Service is not ready",
            errors={"database": "unavailable"},
            status_code=503,
        )
