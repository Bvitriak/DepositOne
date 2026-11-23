from flask import Blueprint

from controllers import dashboard_controller
from utils.auth import token_required
from utils.db import with_db

dashboard_routes = Blueprint("dashboard", __name__)
dashboard_routes.add_url_rule("/api/dashboard", view_func=token_required(with_db(dashboard_controller.overview)), methods=["GET"])
