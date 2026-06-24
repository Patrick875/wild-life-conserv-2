from nacl.utils import random
from users.models import User
from auth.models import Role
from flask_jwt_extended import create_access_token,get_jwt_identity,decode_token
from werkzeug.security import check_password_hash,generate_password_hash
from werkzeug.exceptions import BadRequest,NotFound
from sqlalchemy import or_
from extensions import db
from datetime import datetime,timedelta
from utils.email_service import send_email

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
    
def forgot_password_init(data:dict):
    identifier=data.get("identifier");
    user=User.query.filter(or_(User.email==identifier,User.phone_number==identifier)).first()
    if not user:
        raise NotFound("User not found")
    reset_password_otp=str(random.randint(100000,999999))
    user.reset_password_otp=reset_password_otp
    user.reset_password_otp_expires=datetime.utcnow()+timedelta(minutes=10)
    
    send_email(
        subject="Password Reset OTP",
        recipients=[user.email],
        template="reset_password_otp",
        values={
            "full_name": user.full_name,
            "otp": reset_password_otp
        }
    )
    return {
        "message":"Password reset OTP sent to your email",
        "expires_at":user.reset_password_otp_expires
    }

def password_reset_verify(data:dict):
    identifier=data.get("identifier")
    otp=data.get("otp")
    user=User.query.filter(or_(User.email==identifier,User.phone_number==identifier)).first()
    if not user:
        raise NotFound("User not found")
    if user.reset_password_otp!=otp:
        raise BadRequest("Invalid OTP")
    if user.reset_password_otp_expires<datetime.utcnow():
        raise BadRequest("OTP expired")
    
    reset_token=create_access_token(identity=str(user.id),additional_claims={
        "role":user.role.name,
        "expires_delta":timedelta(minutes=15)
    })
    return {
       "reset_token": reset_token
    }

def password_reset(data:dict):
    reset_token=data.get("reset_token")
    new_password=data.get("new_password")
    if not reset_token or not new_password:
        raise BadRequest("Invalid request")
    #check if the reset token is valid and not expired
    user_id=None
   
    try:
        decoded_token=decode_token(reset_token)
        #get user_id and expires_delta from the decoded token
        user_id=decoded_token.get("sub")
        expires_delta=decoded_token.get("expires_delta")
        if not user_id or not expires_delta:
            raise BadRequest("Invalid reset token")
        #check if the token is expired
        if datetime.utcnow()>datetime.utcfromtimestamp(decoded_token.get("exp")):
            raise BadRequest("Reset token expired")
    except:
        raise BadRequest("Invalid or expired reset token")
    
    user=User.query.get(user_id)
    if not user:
        raise NotFound("User not found")
    user.password_hash=generate_password_hash(new_password)
    user.reset_password_otp=None
    user.reset_password_otp_expires=None
    send_email(
        subject='Password Reset Successful',
        email_template='password_reset_success',
        recipients=[user.email],
        values={
            "full_name": user.full_name,
        }
        )
    db.session.commit()
    return {
        "message":"Password reset successful"
    }