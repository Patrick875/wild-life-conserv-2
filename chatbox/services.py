from typing import Optional

from extensions import db
from chatbox.helpers import chat_with_gemini, chat_with_history_gemini
from chatbox.models import Conversation, AIMessage


SUPPORTED_MODELS = ["gemini"]
SUPPORTED_MODES = ["with_history", "without_history"]


def create_conversation(user_id: int, title: Optional[str] = None):
    conversation = Conversation(
        user_id=user_id,
        title=title or "New conversation",
    )

    db.session.add(conversation)
    db.session.commit()

    return conversation


def get_conversation_by_id(conversation_id: int, user_id: int):
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id,
    ).first()

    if not conversation:
        raise ValueError("Conversation not found")

    return conversation


def generate_conversation_title(content: str):
    if not content:
        return "New conversation"

    title = content.strip()

    if len(title) > 50:
        title = title[:50] + "..."

    return title


def create_ai_message(
    conversation_id: int,
    role: str,
    content: str,
    model: Optional[str] = None,
    tokens_used: int = 0,
):
    message = AIMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        model=model,
        tokens_used=tokens_used,
    )

    db.session.add(message)
    db.session.commit()

    return message


def get_past_conversations(user_id: int):
    conversations = (
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    return [conversation.to_dict() for conversation in conversations]


def get_messages_per_conversation(conversation_id: int, limit: int = 10):
    messages = (
        AIMessage.query
        .filter_by(conversation_id=conversation_id)
        .order_by(AIMessage.created_at.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def get_chats_per_user_conversation(user_id: int, conversation_id: int):
    conversation = get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    messages = (
        AIMessage.query
        .filter_by(conversation_id=conversation.id)
        .order_by(AIMessage.created_at.asc())
        .all()
    )

    return [message.to_dict() for message in messages]


def send_chat(
    user_id: int,
    content: str,
    model: str = "gemini",
    mode: str = "with_history",
    conversation_id: Optional[int] = None,
):
    if model not in SUPPORTED_MODELS:
        raise ValueError("Unsupported AI model")

    if mode not in SUPPORTED_MODES:
        raise ValueError("Please select a valid mode")

    if not content or not content.strip():
        raise ValueError("Message content is required")

    content = content.strip()

    try:
        if conversation_id:
            conversation = get_conversation_by_id(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        else:
            conversation = create_conversation(
                user_id=user_id,
                title=generate_conversation_title(content),
            )

        user_message = create_ai_message(
            conversation_id=conversation.id,
            role="user",
            content=content,
            model=None,
            tokens_used=0,
        )

        if model == "gemini":
            if mode == "without_history":
                ai_response = chat_with_gemini(
                    text=content,
                    conversation_id=conversation.id,
                )
            else:
                history = get_messages_per_conversation(
                    conversation_id=conversation.id,
                    limit=10,
                )

                ai_response = chat_with_history_gemini(
                    conversation_id=conversation.id,
                    text=content,
                    history=history,
                )

        assistant_message = create_ai_message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response.get("response", ""),
            model=model,
            tokens_used=ai_response.get("total_tokens_used", 0),
        )
        
        return {
            "conversation": conversation.to_dict(),
            "user_message": user_message.to_dict(),
            "assistant_message": assistant_message.to_dict(),
            "tokens": {
                "prompt_tokens": ai_response.get("prompt_tokens", 0),
                "response_tokens": ai_response.get("response_tokens", 0),
                "total_tokens_used": ai_response.get("total_tokens_used", 0),
            },
        }

    except Exception as e:
        db.session.rollback()
        raise ValueError(str(e))