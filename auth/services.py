from auth.models import Role, Permission
from users.models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

def login(data:dict):
    username=data["username"]
    password=data["password"]

    user= User.query.filter(User.username==username).first()
    if not user or not check_password_hash(user.password,password):
        raise ValueError("Invalid username and password")
    
    token=create_access_token(identity=user.id,additional_claims={
        "email":user.email,
        "role":user.role
    })
    return {
        "access_token":token
    }
    