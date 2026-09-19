from flask import Blueprint

from controllers import profile_controller
from utils.auth import token_required
from utils.db import with_db

profile_routes = Blueprint("profile", __name__)
profile_routes.add_url_rule("/api/profile", view_func=token_required(with_db(profile_controller.get_profile)), methods=["GET"])
profile_routes.add_url_rule("/api/profile/token", view_func=token_required(with_db(profile_controller.release_token)), methods=["POST"])
