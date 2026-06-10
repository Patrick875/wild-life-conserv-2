import os
import requests
from typing import Optional


gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured")

GEMINI_REQUEST_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={gemini_api_key}"
)

GEMINI_HEADERS = {
    "Content-Type": "application/json"
}


def chat_with_gemini(
    text: str,
    conversation_id: Optional[int] = None,
) -> dict:
    try:
        response = requests.post(
            GEMINI_REQUEST_URL,
            headers=GEMINI_HEADERS,
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    }
                ]
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No response candidates returned by Gemini")

        answer = (
            candidates[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        usage = data.get("usageMetadata", {})

        return {
            "conversation_id": conversation_id,
            "response": answer,
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "response_tokens": usage.get("candidatesTokenCount", 0),
            "total_tokens_used": usage.get("totalTokenCount", 0),
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Gemini request failed: {str(e)}")

    except Exception as e:
        raise ValueError(f"Gemini error: {str(e)}")
    

def build_gemini_contents(text: str, history: Optional[list[dict]] = None):
    contents = []

    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content")

            if not content:
                continue

            gemini_role = "model" if role == "assistant" else "user"

            contents.append({
                "role": gemini_role,
                "parts": [
                    {
                        "text": content
                    }
                ]
            })

    contents.append({
        "role": "user",
        "parts": [
            {
                "text": text
            }
        ]
    })

    return contents


def chat_with_history_gemini(
    text: str,
    conversation_id: Optional[int] = None,
    history: Optional[list[dict]] = None,
) -> dict:
    try:
        response = requests.post(
            GEMINI_REQUEST_URL,
            headers=GEMINI_HEADERS,
            json={
                "contents": build_gemini_contents(text, history)
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No response candidates returned by Gemini")

        answer = (
            candidates[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        usage = data.get("usageMetadata", {})

        return {
            "conversation_id": conversation_id,
            "response": answer,
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "response_tokens": usage.get("candidatesTokenCount", 0),
            "total_tokens_used": usage.get("totalTokenCount", 0),
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Gemini request failed: {str(e)}")

    except Exception as e:
        raise ValueError(f"Gemini error: {str(e)}")