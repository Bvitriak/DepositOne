import bcrypt
import psycopg

from repositories import user_repository
from utils.auth import create_access_token


def register(connection, username, email, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        user = user_repository.create(connection, username, email, password_hash)
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        return {"error": "email or username already exists"}, 409
    return {"access_token": create_access_token(user)}, 201


def login(connection, email, password):
    user = user_repository.find_by_email(connection, email)
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return {"error": "invalid email or password"}, 401
    user_repository.update_last_visit(connection, user.id)
    return {"access_token": create_access_token(user)}, 200


def reset_check(connection, email):
    user = user_repository.find_by_email(connection, email)
    if not user:
        return {"error": "no account with this email"}, 404
    return {"exists": True}, 200


def reset_confirm(connection, email, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    updated = user_repository.update_password(connection, email, password_hash)
    if not updated:
        return {"error": "no account with this email"}, 404
    return {"updated": True}, 200
