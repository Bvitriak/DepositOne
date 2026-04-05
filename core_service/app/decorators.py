from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required_page(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Необходимо войти в систему.", "error")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper
