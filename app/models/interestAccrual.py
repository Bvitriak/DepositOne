from datetime import date
from app.db import db

class InterestAccrual(db.Model):
    __tablename__ = "interestAccruals"

    id = db.Column(db.Integer, primary_key=True)

    deposit_id = db.Column(
        db.Integer,
        db.ForeignKey("deposits.id"),
        nullable=False
    )

    accrual_date = db.Column(db.Date, nullable=False, default=date.today)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)

    interest_amount = db.Column(db.Numeric(12, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)

    is_paid = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<InterestAccrual deposit_id={self.deposit_id} amount={self.interest_amount}>"
