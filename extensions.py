from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os 
import pusher

load_dotenv()

db=SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
mail=Mail()

pusher_client=pusher.Pusher(
    app_id=os.getenv("PUSHER_CHANNELS_APP_ID"),
    key=os.getenv("PUSHER_CHANNELS_KEY"),
    secret=os.getenv("PUSHER_CHANNELS_SECRET"),
    cluster=os.getenv("PUSHER_CHANNELS_CLUSTER"),
    ssl=True
)

FEEBACK_CHANNEL='feedback_ch'
WARNING_CHANNEL='warning_ch'