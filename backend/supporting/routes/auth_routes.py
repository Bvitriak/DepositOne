from flask import Blueprint

from controllers import auth_controller
from utils.db import with_db

auth_routes = Blueprint("auth", __name__)
auth_routes.add_url_rule("/api/register", view_func=with_db(auth_controller.register), methods=["POST"])
auth_routes.add_url_rule("/api/login", view_func=with_db(auth_controller.login), methods=["POST"])
auth_routes.add_url_rule("/api/reset-password/check", view_func=with_db(auth_controller.reset_check), methods=["POST"])
auth_routes.add_url_rule("/api/reset-password/confirm", view_func=with_db(auth_controller.reset_confirm), methods=["POST"])
