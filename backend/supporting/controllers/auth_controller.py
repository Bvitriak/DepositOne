from flask import request, jsonify

from services import auth_service


def register(connection):
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not email or not password:
        return jsonify(error="username, email and password are required"), 400
    result, status = auth_service.register(connection, username, email, password)
    return jsonify(result), status


def login(connection):
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400
    result, status = auth_service.login(connection, email, password)
    return jsonify(result), status


def reset_check(connection):
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify(error="email is required"), 400
    result, status = auth_service.reset_check(connection, email)
    return jsonify(result), status


def reset_confirm(connection):
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400
    result, status = auth_service.reset_confirm(connection, email, password)
    return jsonify(result), status
