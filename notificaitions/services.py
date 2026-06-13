import os
import time

import jwt
import requests

from extensions import beams_client


def build_feedback_notification_payload(warning, feedback, sender):
    sender_name = sender.to_dict().get("full_name") or "Someone"

    return {
        "type": "warning.feedback.created",
        "title": "New feedback on your warning",
        "body": f"{sender_name} replied to your warning",
        "message": f"{sender_name} replied to your warning",
        "warningId": str(warning.id),
        "feedbackId": str(feedback.id),
        "replyCount": warning.feedback_count,
        "senderId": str(sender.id),
        "senderName": sender_name,
        "feedbackMessage": feedback.message,
        "createdAt": feedback.created_at
        if feedback.created_at else None,
    }


def build_beams_publish_body(payload):
    title = payload.get("title") or "Wildlife warning"
    body = payload.get("body") or payload.get("message") or ""
    data = {
        key: "" if value is None else str(value)
        for key, value in payload.items()
    }

    return {
        "web": {
            "notification": {
                "title": title,
                "body": body,
                "deep_link": payload.get("deepLink", "/"),
            },
            "data": data,
        },
        "fcm": {
            "notification": {
                "title": title,
                "body": body,
            },
            "data": data,
        },
        "apns": {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body,
                }
            },
            "data": data,
        },
    }


def generate_beams_token(user_id):
    if beams_client:
        return beams_client.generate_token(str(user_id))

    instance_id = os.getenv("PUSHER_BEAMS_INSTANCE_ID")
    secret_key = os.getenv("PUSHER_BEAMS_SECRET_KEY")
    if not instance_id or not secret_key:
        raise ValueError("Pusher Beams is not configured")

    claims = {
        "iss": f"https://{instance_id}.pushnotifications.pusher.com",
        "sub": str(user_id),
        "exp": int(time.time()) + 24 * 60 * 60,
    }
    token = jwt.encode(claims, secret_key, algorithm="HS256")
    return {"token": token}


def publish_beams_to_users(user_ids, payload):
    normalized_user_ids = [str(user_id) for user_id in user_ids if user_id]
    if not normalized_user_ids:
        return None

    publish_body = build_beams_publish_body(payload)
    if beams_client:
        return beams_client.publish_to_users(
            user_ids=normalized_user_ids,
            publish_body=publish_body,
        )

    return _publish_beams_rest("users", {"users": normalized_user_ids, **publish_body})


def publish_beams_to_interests(interests, payload):
    normalized_interests = [interest for interest in interests if interest]
    if not normalized_interests:
        return None

    publish_body = build_beams_publish_body(payload)
    if beams_client:
        return beams_client.publish_to_interests(
            interests=normalized_interests,
            publish_body=publish_body,
        )

    return _publish_beams_rest(
        "interests",
        {"interests": normalized_interests, **publish_body},
    )


def _publish_beams_rest(publish_type, body):
    instance_id = os.getenv("PUSHER_BEAMS_INSTANCE_ID")
    secret_key = os.getenv("PUSHER_BEAMS_SECRET_KEY")
    if not instance_id or not secret_key:
        raise ValueError("Pusher Beams is not configured")

    response = requests.post(
        f"https://{instance_id}.pushnotifications.pusher.com"
        f"/publish_api/v1/instances/{instance_id}/publishes/{publish_type}",
        headers={
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=15,
    )
    if not response.ok:
        raise ValueError(f"Pusher Beams publish failed: {response.status_code} {response.text}")

    return response.json() if response.text else {"success": True}
