from datetime import datetime, timezone
from app.db import db

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    deposit_id = db.Column(
        db.Integer,
        db.ForeignKey("deposits.id"),
        nullable=False
    )

    operation_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    operation_date = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    description = db.Column(db.String(255), nullable=True)

    cashier_name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.operation_type} {self.amount}>"
