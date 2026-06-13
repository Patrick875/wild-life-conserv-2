from users.models import User

def get_all_users():
    users= User.query.all()
    users_normalized= [user.to_dict() for user in users]
    return users_normalized