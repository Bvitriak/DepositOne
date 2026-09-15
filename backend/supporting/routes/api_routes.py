from flask import Blueprint

from controllers import api_controller
from utils.auth import token_required

api_routes = Blueprint("api", __name__)
api_routes.add_url_rule("/api/apis", view_func=token_required(api_controller.list_apis), methods=["GET"])
