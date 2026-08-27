import os 
from dotenv import load_dotenv

load_dotenv()

def get_database_uri():
    database_uri = os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('DATABASE_URL')

    if not database_uri:
        return database_uri

    if database_uri.startswith(('redis://', 'rediss://')):
        raise ValueError(
            'SQLALCHEMY_DATABASE_URI/DATABASE_URL must be a PostgreSQL URL. '
            'Put your Render Redis URL in REDIS_URL instead.'
        )

    database_uri = database_uri.replace(
        'postgresql.pyscopg2', 'postgresql+psycopg2'
    ).replace(
        'postgresql.pyscopy2', 'postgresql+psycopg2'
    ).replace(
        'postgres://', 'postgresql+psycopg2://', 1
    )

    is_render_external_url = 'render.com' in database_uri and '-postgres.render.com' in database_uri
    ssl_requested = os.getenv('DATABASE_SSL', '').lower() == 'true'

    if 'sslmode=' not in database_uri and (ssl_requested or is_render_external_url):
        separator = '&' if '?' in database_uri else '?'
        database_uri = f'{database_uri}{separator}sslmode=require'

    return database_uri

def database_needs_ssl():
    database_uri = get_database_uri() or ''
    is_render_external_url = 'render.com' in database_uri and '-postgres.render.com' in database_uri
    ssl_requested = os.getenv('DATABASE_SSL', '').lower() == 'true'
    return ssl_requested or is_render_external_url

class Config():
    PORT=os.getenv('PORT',4800)
    FLASK_DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    if database_needs_ssl():
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'sslmode': 'require',
        }
    JWT_TOKEN_LOCATION = os.getenv('JWT_TOKEN_LOCATION')
    JWT_REFRESH_COOKIE_NAME = os.getenv('JWT_REFRESH_COOKIE_NAME')
    JWT_COOKIE_SECURE = False 
    JWT_COOKIE_SAMESITE = os.getenv('JWT_COOKIE_SAMESITE')
    JWT_COOKIE_CSRF_PROTECT = True
    REDIS_URL = os.getenv('REDIS_URL')
    RATELIMIT_STORAGE_URI = REDIS_URL
    EMAIL_VERIFICATION_SALT = os.getenv('EMAIL_VERIFICATION_SALT')
    KOBO_TIMEOUT=os.getenv('KOBO_TIMEOUT')
    KOBO_API_TOKEN=os.getenv('KOBO_API_TOKEN')
    KOBO_SERVER_URL=os.getenv("KOBO_SERVER_URL")
    PUSHER_BEAMS_INSTANCE_ID=os.getenv("PUSHER_BEAMS_INSTANCE_ID")
    PUSHER_BEAMS_SECRET_KEY=os.getenv("PUSHER_BEAMS_SECRET_KEY")
    CLOUDINARY_CLOUD_NAME=os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY=os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET=os.getenv("CLOUDINARY_API_SECRET")
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    PUSHER_CHANNELS_APP_ID=os.getenv("PUSHER_CHANNELS_APP_ID")
    PUSHER_CHANNELS_KEY=os.getenv("PUSHER_CHANNELS_KEY")
    PUSHER_CHANNELS_SECRET=os.getenv("PUSHER_CHANNELS_SECRET")
    PUSHER_CHANNELS_CLUSTER=os.getenv("PUSHER_CHANNELS_CLUSTER")
