from flask import Flask 
from dotenv import load_dotenv
from config import Config
from auth.routes import auth_bp
from forms.routes import forms_bp
from media.routes import uploads_bp
from chatbox.routes import chatbox_bp
from warning_feedbacks.routes import feebacks_bp
from extensions import db,migrate,jwt
from datetime import timedelta

load_dotenv()

url_prefix='/api/v1'
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=3)

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
  

    app.url_map.strict_slashes=False
    
    
    app.register_blueprint(auth_bp,url_prefix=url_prefix+"/auth")
    app.register_blueprint(forms_bp,url_prefix=url_prefix+"/forms")
    app.register_blueprint(uploads_bp,url_prefix=url_prefix+"/uploads")
    app.register_blueprint(feebacks_bp,url_prefix=url_prefix+"/warnings/feedbacks")
    app.register_blueprint(chatbox_bp,url_prefix=url_prefix+"/ai")
    
    import database.models

    return app 



