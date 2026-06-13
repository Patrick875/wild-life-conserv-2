from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os 
import collections
from collections import abc as collections_abc

if not hasattr(collections, "Sized"):
    collections.Sized = collections_abc.Sized
if not hasattr(collections, "Iterable"):
    collections.Iterable = collections_abc.Iterable

try:
    import pusher
except ImportError:
    pusher = None

try:
    import pusher_push_notifications
except ImportError:
    pusher_push_notifications = None

load_dotenv()

db=SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
mail=Mail()

pusher_client = None
if pusher:
    pusher_client = pusher.Pusher(
        app_id=os.getenv("PUSHER_CHANNELS_APP_ID"),
        key=os.getenv("PUSHER_CHANNELS_KEY"),
        secret=os.getenv("PUSHER_CHANNELS_SECRET"),
        cluster=os.getenv("PUSHER_CHANNELS_CLUSTER"),
        ssl=True
    )

beams_client = None
if pusher_push_notifications and os.getenv("PUSHER_BEAMS_INSTANCE_ID") and os.getenv("PUSHER_BEAMS_SECRET_KEY"):
    beams_client = pusher_push_notifications.PushNotifications(
        instance_id=os.getenv("PUSHER_BEAMS_INSTANCE_ID"),
        secret_key=os.getenv("PUSHER_BEAMS_SECRET_KEY"),
    )
