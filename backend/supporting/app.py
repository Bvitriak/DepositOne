from flask import Flask, jsonify

from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.api_routes import api_routes


def create_app():
    application = Flask(__name__)
    application.register_blueprint(auth_routes)
    application.register_blueprint(dashboard_routes)
    application.register_blueprint(api_routes)

    @application.errorhandler(500)
    def internal_error(error):
        return jsonify(error="internal server error", fallback=True), 500

    return application


application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8001)
