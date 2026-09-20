from flask import Blueprint

from controllers import notification_controller
from utils.auth import token_required
from utils.db import with_db

notification_routes = Blueprint("notification", __name__)
notification_routes.add_url_rule("/api/notifications", view_func=token_required(with_db(notification_controller.list_notifications)), methods=["GET"])
