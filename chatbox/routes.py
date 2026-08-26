from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from chatbox.services import (
    send_chat,
    get_past_conversations,
    get_chats_per_user_conversation,
)
from utils.api_response import api_response
from extensions import limiter

chatbox_bp = Blueprint("chatbox", __name__)


@chatbox_bp.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required(locations=["headers"])
def chat():
    """Send a message to the Gemini-powered assistant.
    ---
    tags:
      - AI chat
    security:
      - BearerAuth: []
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              example: How can I safely report wildlife near my farm?
            conversation_id:
              type: integer
              description: Existing owned conversation ID. Omit to create a new conversation.
              example: 12
    responses:
      200:
        description: The user message, Gemini response, conversation metadata, and token usage were saved and returned.
      400:
        description: Message content is missing, invalid, or the conversation is not available to the caller.
      401:
        description: A valid bearer token was not supplied.
      500:
        description: The AI service or conversation persistence failed.
    """

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
    """List the authenticated user's persisted AI conversations.
    ---
    tags:
      - AI chat
    security:
      - BearerAuth: []
    responses:
      200:
        description: Conversations fetched successfully, newest first.
      401:
        description: A valid bearer token was not supplied.
      500:
        description: Conversations could not be fetched.
    """

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
    """Get messages in one of the authenticated user's conversations.
    ---
    tags:
      - AI chat
    security:
      - BearerAuth: []
    parameters:
      - name: conversation_id
        in: path
        type: integer
        required: true
        description: Persisted AI conversation identifier.
    responses:
      200:
        description: Conversation messages fetched successfully in chronological order.
      401:
        description: A valid bearer token was not supplied.
      404:
        description: The conversation does not exist or is not owned by the caller.
      500:
        description: Messages could not be fetched.
    """

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
