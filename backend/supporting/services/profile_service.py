from repositories import user_repository
from utils.auth import create_access_token


def format_date(value):
    if not value:
        return "N/A"
    return value.strftime("%d.%m.%Y")


def serialize(user):
    return {
        "account_id": "U-" + str(user.id).zfill(4),
        "nickname": user.username,
        "email": user.email,
        "status": user.status,
        "created": format_date(user.created_at),
        "last_visit": format_date(user.last_visit_at),
    }


def get_profile(connection, user_id):
    user = user_repository.find_by_id(connection, user_id)
    if not user:
        return {"error": "invalid or expired token"}, 401
    return serialize(user), 200


def release_token(connection, user_id):
    user = user_repository.find_by_id(connection, user_id)
    if not user:
        return {"error": "invalid or expired token"}, 401
    return {"access_token": create_access_token(user)}, 200
