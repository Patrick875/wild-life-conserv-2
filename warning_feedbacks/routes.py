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
