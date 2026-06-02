from auth.models import Role, Permission
from users.models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from sqlalchemy import or_


def login(data:dict):
    identifier=data["identifier"]
    password=data["password"]

    user= User.query.filter(or_(User.email==identifier,User.phone_number==identifier)).first()
    if not user or not check_password_hash(user.password,password):
        raise ValueError("Invalid username and password")
    
    token=create_access_token(identity=user.id,additional_claims={
        "email":user.email,
        "role":user.role
    })
    return {
        "access_token":token
    }
    