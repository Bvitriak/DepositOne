from datetime import date
from app.db import db

class Deposit(db.Model):
    __tablename__ = "deposits"

    id = db.Column(db.Integer, primary_key=True)

    depositor_id = db.Column(
        db.Integer,
        db.ForeignKey("depositors.id"),
        nullable=False
    )

    deposit_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)

    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=False)

    term_months = db.Column(db.Integer, nullable=False)
    capitalization = db.Column(db.Boolean, default=False)
    auto_renewal = db.Column(db.Boolean, default=False)

    status = db.Column(db.String(30), nullable=False, default="active")
    currency = db.Column(db.String(10), nullable=False, default="RUB")

    accruals = db.relationship("InterestAccrual", backref="deposit", lazy=True)
    transactions = db.relationship("Transaction", backref="deposit", lazy=True)
    contracts = db.relationship("Contract", backref="deposit", lazy=True)

    def __repr__(self):
        return f"<Deposit id={self.id} amount={self.amount}>"
