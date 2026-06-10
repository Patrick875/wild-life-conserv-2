from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from chatbox.services import (
    send_chat,
    get_past_conversations,
    get_chats_per_user_conversation,
)
from utils.api_response import api_response

chatbox_bp = Blueprint("chatbox", __name__)


@chatbox_bp.route("/chat", methods=["POST"])
@jwt_required(locations=["headers"])
def chat():

    try:
        user_id = int(get_jwt_identity())

        data = request.get_json() or {}

        content = data.get("content")
        
        conversation_id = data.get("conversation_id")

        response = send_chat(
            user_id=user_id,
            content=content,
            model="gemini",
            mode="with_history",
            conversation_id=conversation_id,
        )
        print("ai-response",response)
        return api_response(
            success=True,
            message="Message sent successfully",
            data=response,
            status_code=200,
        )

    except ValueError as e:
        return api_response(
            success=False,
            message=str(e),
            status_code=400,
        )

    except Exception as e:
        return api_response(
            success=False,
            message=str(e),
            status_code=500,
        )

@chatbox_bp.route("/conversations", methods=["GET"])
@jwt_required(locations=["headers"])
def conversations():

    try:
        user_id = int(get_jwt_identity())

        conversations = get_past_conversations(
            user_id=user_id
        )

        return api_response(
            success=True,
            message="Conversations fetched successfully",
            data=conversations,
            status_code=200,
        )

    except Exception as e:
        return api_response(
            success=False,
            message=str(e),
            status_code=500,
        )

@chatbox_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["GET"],
)
@jwt_required(locations=["headers"])
def conversation_messages(conversation_id):

    try:
        user_id = int(get_jwt_identity())

        messages = get_chats_per_user_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
        )

        return api_response(
            success=True,
            message="Messages fetched successfully",
            data=messages,
            status_code=200,
        )

    except ValueError as e:
        return api_response(
            success=False,
            message=str(e),
            status_code=404,
        )

    except Exception as e:
        return api_response(
            success=False,
            message=str(e),
            status_code=500,
        )