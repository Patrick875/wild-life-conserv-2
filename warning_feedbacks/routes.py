from flask import Blueprint,request
from warning_feedbacks.services import (
    add_feedback,
    delete_feedback,
    get_feedback_per_warning,
    update_feedback,
)
from flask_jwt_extended import jwt_required,get_jwt_identity
from warning_feedbacks.schemas import FeedbackSchema
from marshmallow import ValidationError
from utils.api_response import api_response

feebacks_bp=Blueprint('feedbacks',__name__)

@feebacks_bp.route('/',methods=['POST'])
@jwt_required(locations=['headers'])
def create_feedback():
    """Add feedback to a wildlife warning.
    ---
    tags:
      - Warning feedback
    security:
      - BearerAuth: []
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: Feedback payload validated against the warning feedback schema.
        schema:
          type: object
          required:
            - warning_id
            - message
          properties:
            warning_id:
              type: integer
              example: 42
            message:
              type: string
              example: A park guard has been notified and will investigate.
    responses:
      200:
        description: Warning feedback added successfully.
      400:
        description: The feedback payload failed validation.
      401:
        description: A valid bearer token was not supplied.
      500:
        description: Feedback could not be saved.
    """
    try:
        user_id=int(get_jwt_identity())
        data= FeedbackSchema().load(request.json)
        feedback=add_feedback(user_id=user_id,data=data)
        return api_response(
            success=True,
            message='Warning feedback added successfuly',
            data=feedback,
            status_code=200
        )
    except ValidationError as err:
        return api_response(
            success=False,
            message="Validation failed",
            errors=err.messages,
            status_code=400
        )
    except ValueError as e:
        print(e)
        return api_response(
            success=False,
            message="Failed adding feedback",
            errors=str(e),
            status_code=500
        )

@feebacks_bp.route('/<warning_id>',methods=['GET'])
@jwt_required(locations=['headers'])
def get_Warning_feedbacks(warning_id):
    """List feedback associated with one warning.
    ---
    tags:
      - Warning feedback
    security:
      - BearerAuth: []
    parameters:
      - name: warning_id
        in: path
        type: integer
        required: true
        description: Local wildlife warning identifier.
    responses:
      200:
        description: Warning feedback fetched successfully.
      401:
        description: A valid bearer token was not supplied.
      500:
        description: Feedback could not be fetched.
    """
    try:
        warn_id=int(warning_id)
        warnings=get_feedback_per_warning(warning_id=warn_id)
        return api_response(
            success=True,
            message='Warning fetched successfuly',
            data=warnings,
            status_code=200
        )
    except ValueError as e:
        print(str(e))
        return api_response(
            success=False,
            message="Failed fetching feedback",
            errors=str(e),
            status_code=500
        )


@feebacks_bp.route('/items/<int:feedback_id>', methods=['PUT', 'PATCH'])
@jwt_required(locations=['headers'])
def update_warning_feedback(feedback_id):
    """Update an existing warning-feedback item.
    ---
    tags:
      - Warning feedback
    security:
      - BearerAuth: []
    consumes:
      - application/json
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
        description: Feedback record identifier.
      - name: body
        in: body
        required: true
        description: Fields to update on the feedback item.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Rangers are on their way to the reported location.
    responses:
      200:
        description: Warning feedback updated successfully.
      401:
        description: A valid bearer token was not supplied.
      403:
        description: The caller does not have permission to update this feedback.
      400:
        description: The update payload is invalid.
      500:
        description: Feedback could not be updated.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        feedback = update_feedback(
            user_id=user_id,
            feedback_id=feedback_id,
            data=data,
        )
        return api_response(
            success=True,
            message='Warning feedback updated successfully',
            data=feedback,
            status_code=200
        )
    except PermissionError as e:
        return api_response(success=False, message=str(e), status_code=403)
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=400)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)


@feebacks_bp.route('/items/<int:feedback_id>', methods=['DELETE'])
@jwt_required(locations=['headers'])
def delete_warning_feedback(feedback_id):
    """Delete an existing warning-feedback item.
    ---
    tags:
      - Warning feedback
    security:
      - BearerAuth: []
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
        description: Feedback record identifier.
    responses:
      200:
        description: Warning feedback deleted successfully.
      401:
        description: A valid bearer token was not supplied.
      403:
        description: The caller does not have permission to delete this feedback.
      404:
        description: The feedback item does not exist.
      500:
        description: Feedback could not be deleted.
    """
    try:
        user_id = int(get_jwt_identity())
        delete_feedback(user_id=user_id, feedback_id=feedback_id)
        return api_response(
            success=True,
            message='Warning feedback deleted successfully',
            status_code=200
        )
    except PermissionError as e:
        return api_response(success=False, message=str(e), status_code=403)
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=404)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)
