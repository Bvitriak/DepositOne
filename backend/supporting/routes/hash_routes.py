from flask import Blueprint

from controllers import hash_controller

hash_routes = Blueprint("hash", __name__)
hash_routes.add_url_rule("/api/hash/<path:value>", view_func=hash_controller.get_hash, methods=["GET"])
