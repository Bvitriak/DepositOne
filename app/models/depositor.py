from datetime import datetime, timezone
from app.db import db

class Depositor(db.Model):
    __tablename__ = "depositors"

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)

    passport_series = db.Column(db.String(10), nullable=False)
    passport_number = db.Column(db.String(20), nullable=False, unique=True)
    issued_by = db.Column(db.String(255), nullable=True)

    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    deposits = db.relationship("Deposit", backref="depositor", lazy=True)
    contracts = db.relationship("Contract", backref="depositor", lazy=True)

    def __repr__(self):
        return f"<Depositor {self.last_name} {self.first_name}>"
