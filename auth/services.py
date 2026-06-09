from users.models import User
from auth.models import Role
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy import or_
from extensions import db

def login(data: dict):
    identifier = data["identifier"]
    password = data["password"]

    user = User.query.filter(or_(User.email == identifier, User.phone_number == identifier)).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid username and password")
    
    user_dict=user.to_dict()

    return {
        "access_token": create_access_token(identity=str(user.id),additional_claims={
            "role":user_dict.get("role")
        }),
        "user":{
            "fullName":user_dict.get("full_name"),
            "userName":user_dict.get("username"),
            "organization":user_dict.get("organization"),
            "occupation":user_dict.get("occupation"),
            "phoneNumber":user_dict.get("phone_number"),
            "email":user_dict.get("email"),
            "role":user_dict.get("role")
        }
    }

def signup_user(data:dict):
    full_name=data.get('fullName')
    email=data.get('email')
    phone=data.get('phoneNumber')
    role=data.get('role')
    occupation=data.get('occupation')
    organization=data.get('organization')
    password=data.get("password")

    user_exists= User.query.filter(or_(User.phone_number==phone,User.email==email)).first()
    print(user_exists)
    if user_exists:
        raise ValueError("User already exists please proceed to login or reset password")
    role=Role.query.filter_by(name=role).first()
    if not role:
        raise ValueError("Failed invalid form data")
    role_id=role.id
    password_hash=generate_password_hash(password)

    user=User(
        full_name=full_name,
        username=phone,
        email=email,
        phone_number=phone,
        role_id=role_id,
        password_hash=password_hash,
        occupation=occupation,
        organization=organization,
        is_active=True,
        is_verified=True
    )

    db.session.add(user)
    db.session.commit()

    return {
        "user_id":user.to_dict()["id"],
    }
    