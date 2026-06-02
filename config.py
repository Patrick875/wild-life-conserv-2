import os 
from dotenv import load_dotenv

load_dotenv()

class Config():
    PORT=os.getenv('PORT',4800)
    FLASK_DEBUG=True
    SECRET_KEY=os.getenv('SECRET_KEY')
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
    JWT_TOKEN_LOCATION =os.getenv('JWT_TOKEN_LOCATION')
    JWT_REFRESH_COOKIE_NAME = os.getenv('JWT_REFRESH_COOKIE_NAME')
    JWT_COOKIE_SECURE = False 
    JWT_COOKIE_SAMESITE = os.getenv('JWT_COOKIE_SAMESITE')
    JWT_COOKIE_CSRF_PROTECT = True
    EMAIL_VERIFICATION_SALT = os.getenv('EMAIL_VERIFICATION_SALT')
    KOBO_TIMEOUT=os.getenv('KOBO_TIMEOUT')
    KOBO_API_TOKEN=os.getenv('KOBO_API_TOKEN')
    KOBO_SERVER_URL=os.getenv("KOBO_SERVER_URL")