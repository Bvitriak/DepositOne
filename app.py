import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from core_service.app.api import register_api_routes
from core_service.app.auth import register_auth_routes
from core_service.app.config.config import get_flask_config
from core_service.app.db import teardown_db
from core_service.app.models.user import User
from core_service.app.routes.routes_register import register_routes
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CORE_APP_DIR = BASE_DIR / "core_service" / "app"

def create_app() -> Flask:
    flask_app = Flask(__name__, template_folder=str(CORE_APP_DIR / "templates"), static_folder=str(CORE_APP_DIR / "static"))
    flask_app.config.update(get_flask_config())
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.login_message = "Сначала выполните вход."
    login_manager.init_app(flask_app)
    JWTManager(flask_app)

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.get_by_id(int(user_id))
        except (TypeError, ValueError):
            return None

    @flask_app.teardown_appcontext
    def on_teardown(exception):
        teardown_db(exception)

    register_auth_routes(flask_app)
    register_api_routes(flask_app)
    register_routes(flask_app)
    return flask_app

if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=debug)
