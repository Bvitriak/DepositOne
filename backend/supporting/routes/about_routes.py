from flask import Blueprint

from controllers import about_controller

about_routes = Blueprint("about", __name__)
about_routes.add_url_rule("/api/about", view_func=about_controller.get_about, methods=["GET"])
