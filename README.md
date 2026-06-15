# Wildlife Warning Backend

A Flask backend for a wildlife warning and response platform. The API supports user authentication, KoboToolbox-backed warning submissions, feedback on warnings, media uploads, realtime notifications, push notifications, and an AI chat assistant for in-app support.

The project is designed as the server layer for mobile or web clients used by farmers, park guards, and administrators who need to report wildlife incidents, track submissions, respond to warnings, and receive timely updates.

## What It Provides

- JWT-based authentication for registered users.
- Role-aware user records for farmers, park guards, and administrators.
- KoboToolbox integration for form discovery, warning submission, and submission sync.
- Local warning records with feedback threads.
- Cloudinary-powered file uploads for images, videos, and documents.
- Pusher Channels support for realtime private user events.
- Pusher Beams support for push notifications.
- AI chat conversations with stored message history.
- Gemini as the default LLM provider, with the chat service structured so another provider can be added behind the same interface.
- PostgreSQL persistence through SQLAlchemy.
- Alembic/Flask-Migrate database migrations.
- Seed commands for roles, permissions, and initial users.

## Core Integrations

### KoboToolbox

KoboToolbox is used for survey/form workflows. The backend can fetch forms, read form details, submit warning data, and keep local warning records linked to Kobo form and submission IDs.

Relevant environment variables:

```env
KOBO_SERVER_URL=
KOBO_API_TOKEN=
KOBO_TIMEOUT=15
```

### Cloudinary

Uploads are handled through Cloudinary. The upload service validates supported media types, sends files to Cloudinary, and stores provider metadata such as public ID, optimized URL, file type, dimensions, size, and upload status.

Relevant environment variables:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### Pusher

Pusher Channels is used for realtime private user events, such as notifying a warning owner when feedback is added.

Pusher Beams is used for push notifications. Beams auth is exposed for logged-in clients, and server-side notification helpers can publish user-targeted pushes.

Relevant environment variables:

```env
PUSHER_CHANNELS_APP_ID=
PUSHER_CHANNELS_KEY=
PUSHER_CHANNELS_SECRET=
PUSHER_CHANNELS_CLUSTER=
PUSHER_BEAMS_INSTANCE_ID=
PUSHER_BEAMS_SECRET_KEY=
```

### AI Chat

The AI chat feature stores conversations and messages in the database. Gemini is the default provider, currently using Gemini 2.5 Flash through the Google Generative Language API.

The chat service accepts a model argument internally and isolates provider-specific calls in helper functions, so another LLM can be added without changing the rest of the chat workflow.

Relevant environment variable:

```env
GEMINI_API_KEY=
```

## Tech Stack

- Python 3.11
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- PostgreSQL
- Marshmallow
- Cloudinary
- Pusher Channels and Beams
- Google Gemini API
- Gunicorn

## Project Structure

```text
auth/                 Authentication routes, schemas, and services
chatbox/              AI conversation models, routes, and provider helpers
database/             Base models and seeders
forms/                KoboToolbox form and submission integration
media/                Cloudinary upload handling
notificaitions/       Pusher Channels and Beams helpers
users/                User routes, models, and services
warning/              Warning models, routes, and services
warning_feedbacks/    Feedback models, routes, and services
migrations/           Alembic migration files
app.py                Flask application factory
run.py                Local app entrypoint and CLI seed commands
```

Note: the notifications package is currently named `notificaitions` in the codebase, so imports use that spelling.

## Getting Started

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file with the required values for your database and integrations:

```env
PORT=4800
FLASK_DEBUG=True
SECRET_KEY=
JWT_SECRET_KEY=
JWT_TOKEN_LOCATION=headers
SQLALCHEMY_DATABASE_URI=

KOBO_SERVER_URL=
KOBO_API_TOKEN=
KOBO_TIMEOUT=15

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

PUSHER_CHANNELS_APP_ID=
PUSHER_CHANNELS_KEY=
PUSHER_CHANNELS_SECRET=
PUSHER_CHANNELS_CLUSTER=
PUSHER_BEAMS_INSTANCE_ID=
PUSHER_BEAMS_SECRET_KEY=

GEMINI_API_KEY=
```

Run migrations:

```bash
flask db upgrade
```

Seed roles, permissions, and initial users:

```bash
flask --app run.py seed-all
```

Start the development server:

```bash
python run.py
```

The API is mounted under:

```text
/api/v1
```

## Deployment

The included Dockerfile installs dependencies, runs database migrations, runs seeders, and starts Gunicorn:

```bash
gunicorn -c gunicorn_config.py run:app
```

For platforms like Render, make sure all required environment variables are configured and that the database is reachable from the deployed service.

## API Areas

- `/api/v1/auth` for registration and login.
- `/api/v1/users` for user listing.
- `/api/v1/forms` for Kobo form and submission workflows.
- `/api/v1/uploads` for Cloudinary uploads.
- `/api/v1/warnings` for warning records.
- `/api/v1/warnings/feedbacks` for warning feedback.
- `/api/v1/pusher` for Pusher Channels and Beams auth.
- `/api/v1/ai` for AI chat conversations and messages.

## Notes for Contributors

- Keep integration-specific code inside service/helper modules so routes stay thin.
- Preserve the API response shape from `utils/api_response.py`.
- Keep AI provider logic behind the chat service boundary so Gemini can remain the default without locking the app to one LLM.
- Avoid committing secrets or environment-specific values.
