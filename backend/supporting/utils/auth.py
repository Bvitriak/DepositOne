from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import request, jsonify, g

import config


def create_access_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.now(timezone.utc) + config.ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token):
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])


def token_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="authorization required"), 401
        token = header[len("Bearer "):]
        try:
            payload = decode_access_token(token)
        except jwt.PyJWTError:
            return jsonify(error="invalid or expired token"), 401
        g.user = {"id": payload["user_id"], "username": payload["username"]}
        return view(*args, **kwargs)
    return wrapper
