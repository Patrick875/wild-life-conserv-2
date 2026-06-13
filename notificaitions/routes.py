from flask import Blueprint,request
from flask_jwt_extended import jwt_required,get_jwt_identity
from utils.api_response import api_response
from extensions import pusher_client
from notificaitions.services import (
    generate_beams_token,
)
pusher_bp=Blueprint("pusher_bp",__name__)

@pusher_bp.route('/auth',methods=["POST"])
@jwt_required(locations=["headers"])
def pusher_authentication():
    current_user_id = get_jwt_identity()
    
    channel_name = request.form.get("channel_name")
    socket_id = request.form.get("socket_id")

    if not current_user_id:
        return api_response(
            success=False,
            status_code=401,
            message='User not logged in please login',
        )
        
    if not channel_name or not socket_id:
        return api_response(
            success=False,
            status_code=400,
            message='Missing required parameters: channel_name or socket_id',
        )

    expected_channel = f"private-user-{current_user_id}"

    if channel_name != expected_channel:
        return api_response( 
            success=False,
            message="Unauthorized to access this channel",
            status_code=403
        )

    try:
        if not pusher_client:
            return api_response(success=False, message="Pusher Channels is not configured", status_code=503)

        # Generates standard dict: {"auth": "your_api_key:signature_hash"}
        auth_response = pusher_client.authenticate(
            channel=channel_name,
            socket_id=socket_id
        )
        # Wrap safely inside your custom API standard response
        return api_response(success=True, data=auth_response,message="Pusher user successful", status_code=200) 
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)


@pusher_bp.route('/beams/auth', methods=["GET", "POST"])
@jwt_required(locations=["headers"])
def pusher_beams_authentication():
    try:
        current_user_id = get_jwt_identity()
        token = generate_beams_token(current_user_id)
        return api_response(
            success=True,
            data=token,
            message="Pusher Beams token generated successfully",
            status_code=200,
        )
    except ValueError as e:
        return api_response(success=False, message=str(e), status_code=503)
    except Exception as e:
        return api_response(success=False, message=str(e), status_code=500)
