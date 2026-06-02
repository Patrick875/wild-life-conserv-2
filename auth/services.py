from users.models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from sqlalchemy import or_


def login(data: dict):
    identifier = data["identifier"]
    password = data["password"]

    user = User.query.filter(or_(User.email == identifier, User.phone_number == identifier)).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid username and password")

    return {
        "access_token": create_access_token(identity=user.id)
    }
    