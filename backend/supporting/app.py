import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import psycopg
from flask import Flask, request, jsonify
from flask_cors import CORS

import database

application = Flask(__name__)
CORS(application)

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = timedelta(hours=1)


def make_access_token(user):
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@application.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not email or not password:
        return jsonify(error="username, email and password are required"), 400
    try:
        connection = database.connect()
    except psycopg.OperationalError:
        return jsonify(error="database unavailable", fallback=True), 503
    try:
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id, username",
                    (username, email, password_hash),
                )
                row = cursor.fetchone()
                connection.commit()
            except psycopg.errors.UniqueViolation:
                connection.rollback()
                return jsonify(error="email or username already exists"), 409
        access_token = make_access_token({"id": row[0], "username": row[1]})
    finally:
        connection.close()
    return jsonify(access_token=access_token), 201


@application.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400
    try:
        connection = database.connect()
    except psycopg.OperationalError:
        return jsonify(error="database unavailable", fallback=True), 503
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE email = %s",
                (email,),
            )
            row = cursor.fetchone()
        if not row or not bcrypt.checkpw(password.encode(), row[2].encode()):
            return jsonify(error="invalid email or password"), 401
        access_token = make_access_token({"id": row[0], "username": row[1]})
    finally:
        connection.close()
    return jsonify(access_token=access_token)


@application.post("/api/reset-password/check")
def reset_password_check():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify(error="email is required"), 400
    try:
        connection = database.connect()
    except psycopg.OperationalError:
        return jsonify(error="database unavailable", fallback=True), 503
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
    finally:
        connection.close()
    if not row:
        return jsonify(error="no account with this email"), 404
    return jsonify(exists=True)


@application.post("/api/reset-password/confirm")
def reset_password_confirm():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400
    try:
        connection = database.connect()
    except psycopg.OperationalError:
        return jsonify(error="database unavailable", fallback=True), 503
    try:
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (password_hash, email),
            )
            updated = cursor.rowcount
            connection.commit()
    finally:
        connection.close()
    if not updated:
        return jsonify(error="no account with this email"), 404
    return jsonify(updated=True)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8001)
