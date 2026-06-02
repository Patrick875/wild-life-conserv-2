from flask import Flask 
from dotenv import load_dotenv
from config import Config
from auth.routes import auth_bp
from forms.routes import forms_bp
from extensions import db,migrate,jwt

load_dotenv()

url_prefix='/api/v1'
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
    
    app.register_blueprint(auth_bp,url_prefix=url_prefix+"/auth")
    app.register_blueprint(forms_bp,url_prefix=url_prefix+"/forms")

    import database.models

    return app 



