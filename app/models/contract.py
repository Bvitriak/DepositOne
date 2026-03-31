from datetime import date
from app.db import db

class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)

    contract_number = db.Column(db.String(50), nullable=False, unique=True)
    contract_date = db.Column(db.Date, nullable=False, default=date.today)

    depositor_id = db.Column(
        db.Integer,
        db.ForeignKey("depositors.id"),
        nullable=False
    )

    deposit_id = db.Column(
        db.Integer,
        db.ForeignKey("deposits.id"),
        nullable=False
    )

    term_description = db.Column(db.String(255), nullable=True)
    special_conditions = db.Column(db.Text, nullable=True)
    is_signed = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Contract {self.contract_number}>"
