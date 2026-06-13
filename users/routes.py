from flask import Blueprint, request
from users.services import get_all_users
from utils.api_response import api_response

users_bp=Blueprint("users",__name__)

@users_bp.route("/",methods=["GET"])
def get_app_users():
    all_users=get_all_users()
    return api_response(
        success=True,
        data=all_users,
        status_code=200,
        message='All users fetched successfuly'
    )