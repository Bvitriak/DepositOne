import logging
from http import HTTPStatus
from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from core_service.app.constants import MIN_PASSWORD_LENGTH, REMEMBER_CHECKBOX_VALUE
from core_service.app.db import get_db, refresh_slave_after_write
from core_service.app.models.user import User

logger = logging.getLogger(__name__)

def _fetch_user_by_login(login_value: str):
    db = get_db()
    return db.execute(
        """
        SELECT id, user_name, email, password_hash, token, role, is_active, created_at
        FROM users
        WHERE user_name = ? OR email = ?
        LIMIT 1
        """,
        (login_value, login_value),
    ).fetchone()

def _fetch_user_by_username(username: str):
    db = get_db()
    return db.execute(
        """
        SELECT id, user_name, email, password_hash, token, role, is_active, created_at
        FROM users
        WHERE user_name = ?
        LIMIT 1
        """,
        (username,),
    ).fetchone()

def _validate_password(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Пароль должен содержать минимум {MIN_PASSWORD_LENGTH} символов."
    if password.isdigit() or password.isalpha():
        return "Пароль должен содержать буквы и цифры."
    return None

def register_auth_routes(app):
    @app.route("/auth/register", methods=["GET", "POST"], endpoint="register")
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        if request.method == "GET":
            return render_template("register.html")

        user_name = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""

        if not user_name or not email or not password or not password2:
            flash("Все поля обязательны.", "error")
            return render_template("register.html"), HTTPStatus.BAD_REQUEST

        if password != password2:
            flash("Пароли не совпадают.", "error")
            return render_template("register.html"), HTTPStatus.BAD_REQUEST

        password_error = _validate_password(password)
        if password_error:
            flash(password_error, "error")
            return render_template("register.html"), HTTPStatus.BAD_REQUEST

        db = get_db()
        existing = db.execute(
            """
            SELECT id
            FROM users
            WHERE user_name = ? OR email = ?
            LIMIT 1
            """,
            (user_name, email),
        ).fetchone()
        if existing:
            flash("Пользователь с таким логином или email уже существует.", "error")
            return render_template("register.html"), HTTPStatus.CONFLICT

        password_hash = generate_password_hash(password)
        db.execute(
            """
            INSERT INTO users (user_name, email, password_hash, role, is_active)
            VALUES (?, ?, ?, 'user', 1)
            """,
            (user_name, email, password_hash),
        )
        db.commit()
        refresh_slave_after_write()

        flash("Регистрация выполнена успешно. Теперь войдите в систему.", "success")
        return redirect(url_for("login"))

    @app.route("/auth/login", methods=["GET", "POST"], endpoint="login")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        if request.method == "GET":
            return render_template("login.html")

        login_value = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""
        remember = request.form.get("remember") == REMEMBER_CHECKBOX_VALUE

        if not login_value or not password:
            flash("Введите логин/email и пароль.", "error")
            return render_template("login.html"), HTTPStatus.BAD_REQUEST

        row = _fetch_user_by_login(login_value)
        if row is None or not check_password_hash(row["password_hash"], password):
            flash("Неверный логин/email или пароль.", "error")
            return render_template("login.html"), HTTPStatus.UNAUTHORIZED

        user = User.from_row(row)
        login_user(user, remember=remember)
        flash("Вход выполнен успешно.", "success")
        return redirect(url_for("index"))

    @app.route("/auth/logout", methods=["POST"], endpoint="logout")
    @login_required
    def logout():
        logout_user()
        flash("Вы вышли из системы.", "success")
        return redirect(url_for("login"))

    @app.route("/auth/token", methods=["POST"], endpoint="token")
    def token():
        login_value = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""

        row = _fetch_user_by_login(login_value)
        if row is None or not check_password_hash(row["password_hash"], password):
            abort(HTTPStatus.UNAUTHORIZED)

        access_token = create_access_token(identity=str(row["id"]))
        return jsonify({"access_token": access_token, "token_type": "bearer"})

    @app.route("/auth/issue-token", methods=["POST"], endpoint="issue_token")
    @login_required
    def issue_token():
        access_token = create_access_token(identity=str(current_user.id))
        return jsonify({
            "ok": True,
            "access_token": access_token,
            "token_type": "bearer",
            "username": current_user.username,
        }), 200

    @app.route("/profile/<string:username>", endpoint="profile")
    @login_required
    def user_profile(username: str):
        if username != current_user.username:
            logger.warning(
                "Forbidden profile access attempt: current=%s requested=%s",
                current_user.username,
                username,
            )
            abort(403)

        row = _fetch_user_by_username(username)
        if row is None:
            logger.warning("Profile user not found: username=%s", username)
            abort(404)

        profile_user = {
            "id": row["id"],
            "username": row["user_name"],
            "email": row["email"],
            "role": row["role"],
            "is_active": bool(row["is_active"]),
            "token": row["token"],
            "created_at": row["created_at"],
        }
        return render_template("profile.html", profile_user=profile_user)
