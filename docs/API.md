# Wildlife Warning API Reference

Base URL: `/api/v1`  
Interactive Swagger UI: `/api/docs`  
OpenAPI JSON: `/api/docs/swagger.json`

## Conventions

Protected endpoints require an access token from `POST /auth/login`:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

All responses use the same envelope:

```json
{
  "success": true,
  "message": "Warnings fetched successfully",
  "timestamp": 1760000000,
  "data": {}
}
```

On a failed request, `success` is `false` and `errors` may provide field-level validation or integration details. Timestamps are Unix seconds.

## Operational endpoints

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Liveness probe; confirms the API process is running. |
| `GET` | `/ready` | No | Readiness probe; verifies database connectivity. Returns `503` when unavailable. |

## Authentication and users

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Create a farmer, park guard, or administrator account. |
| `POST` | `/auth/login` | No | Exchange email/phone number and password for a JWT. |
| `GET` | `/users/me` | Required | Fetch the authenticated user's profile and role. |
| `GET` | `/users` | No | List application users. |

Login request:

```json
{ "identifier": "farmer@example.com", "password": "Example1!" }
```

## KoboToolbox forms and submissions

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/forms` | No | List available Kobo survey forms. |
| `GET` | `/forms/{form_uuid}` | No | Fetch a form definition for rendering a dynamic client form. |
| `GET` | `/forms/{form_uuid}/submissions` | Required | Fetch submissions for a Kobo form. |
| `GET` | `/forms/{form_uuid}/submissions/me` | Required | Fetch the caller's submissions for a Kobo form. |
| `POST` | `/forms/{form_uuid}/submit_warning` | Required | Submit a warning to Kobo and persist its local/Kobo linkage. |
| `PUT` | `/forms/{form_uuid}/submissions/{warning_id}` | Required | Update a Kobo-backed warning submission. |
| `DELETE` | `/forms/{form_uuid}/submissions/{warning_id}` | Required | Delete a Kobo-backed warning submission. |

Submission bodies must use the question names and field types defined by the selected Kobo form. The response includes the local warning record and Kobo submission identifiers needed for subsequent updates.

## Warnings, feedback, and uploads

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/warnings?mine=true` | Required | List warnings visible to the caller. Use `mine=true` to restrict to owned warnings. |
| `GET` | `/warnings/{warning_id}` | Required | Fetch one warning, subject to ownership/role permissions. |
| `PATCH` | `/warnings/{warning_id}` | Required | Update a local warning record. `PUT` is also accepted. |
| `DELETE` | `/warnings/{warning_id}` | Required | Delete a local warning record. |
| `POST` | `/warnings/feedbacks` | Required | Add feedback to a warning. |
| `GET` | `/warnings/feedbacks/{warning_id}` | Required | List feedback for a warning. |
| `PATCH` | `/warnings/feedbacks/items/{feedback_id}` | Required | Update feedback owned or permitted for the caller. |
| `DELETE` | `/warnings/feedbacks/items/{feedback_id}` | Required | Delete feedback owned or permitted for the caller. |
| `POST` | `/uploads` | No | Upload a multipart `file` to Cloudinary. |

## AI and notifications

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `POST` | `/ai/chat` | Required | Send `content` and an optional `conversation_id` to the Gemini assistant. |
| `GET` | `/ai/conversations` | Required | List the caller's stored conversations. |
| `GET` | `/ai/conversations/{conversation_id}/messages` | Required | Retrieve messages in one owned conversation. |
| `POST` | `/pusher/auth` | Required | Authenticate a Pusher Channels private-user subscription. |
| `GET` or `POST` | `/pusher/beams/auth` | Required | Generate a Pusher Beams token for the authenticated user. |

Example chat request:

```json
{
  "content": "How should I report an elephant near my farm?",
  "conversation_id": 12
}
```

Omit `conversation_id` to start a new persisted conversation.

## Local development

1. Copy the environment variables listed in the project README into `.env`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run `flask db upgrade`, then `flask --app run.py seed-all`.
4. Start the API with `python run.py` and visit `/api/docs`.

External integrations (KoboToolbox, Cloudinary, Gemini, and Pusher) require their corresponding environment variables. `/health` is safe for process checks; use `/ready` when a deployment platform needs to wait for the database.
