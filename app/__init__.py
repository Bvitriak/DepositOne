from flask import Flask
from app.db import db

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "deposit-bank-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../database/depositBank.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import register_routes
    register_routes(app)

    with app.app_context():
        from app.models.depositor import Depositor
        from app.models.deposit import Deposit
        from app.models.contract import Contract
        from app.models.transaction import Transaction
        from app.models.interestAccrual import InterestAccrual

        db.create_all()

    return app
