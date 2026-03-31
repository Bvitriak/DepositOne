from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app.db import db
from app.models.transaction import Transaction
from app.models.deposit import Deposit
from app.models.depositor import Depositor
from app.models.interestAccrual import InterestAccrual

TWO_PLACES = Decimal("0.01")

def normalize_money(value):
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def get_cash_flow_by_period(start_dt, end_dt):
    income_types = ["deposit_open", "deposit_topup"]
    expense_types = ["deposit_return", "interest_payment"]

    income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.operation_date >= start_dt,
        Transaction.operation_date <= end_dt,
        Transaction.operation_type.in_(income_types)
    ).scalar()

    expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.operation_date >= start_dt,
        Transaction.operation_date <= end_dt,
        Transaction.operation_type.in_(expense_types)
    ).scalar()

    income = normalize_money(income)
    expense = normalize_money(expense)
    balance = (income - expense).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return {
        "start": start_dt,
        "end": end_dt,
        "income": income,
        "expense": expense,
        "balance": balance
    }

def get_today_cash_flow():
    start_dt = datetime.combine(date.today(), datetime.min.time())
    end_dt = datetime.combine(date.today(), datetime.max.time())
    return get_cash_flow_by_period(start_dt, end_dt)

def get_month_cash_flow(year, month):
    start_dt = datetime(year, month, 1)

    if month == 12:
        end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(seconds=1)

    return get_cash_flow_by_period(start_dt, end_dt)

def get_year_cash_flow(year):
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_five_year_cash_flow(start_year):
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(start_year + 5, 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_depositor_report(depositor_id):
    depositor = Depositor.query.get_or_404(depositor_id)

    deposits = Deposit.query.filter_by(depositor_id=depositor_id).all()
    deposit_ids = [deposit.id for deposit in deposits]

    total_deposit_amount = sum((Decimal(str(d.amount)) for d in deposits), Decimal("0.00"))

    total_interest = db.session.query(func.sum(InterestAccrual.interest_amount)).filter(
        InterestAccrual.deposit_id.in_(deposit_ids) if deposit_ids else False
    ).scalar()

    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.deposit_id.in_(deposit_ids) if deposit_ids else False,
        Transaction.operation_type.in_(["deposit_open", "deposit_topup"])
    ).scalar()

    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.deposit_id.in_(deposit_ids) if deposit_ids else False,
        Transaction.operation_type.in_(["deposit_return", "interest_payment"])
    ).scalar()

    return {
        "depositor_id": depositor.id,
        "full_name": f"{depositor.last_name} {depositor.first_name} {depositor.middle_name or ''}".strip(),
        "deposits_count": len(deposits),
        "total_deposit_amount": normalize_money(total_deposit_amount),
        "total_interest": normalize_money(total_interest),
        "total_income": normalize_money(total_income),
        "total_expense": normalize_money(total_expense)
    }

def get_all_depositors_summary():
    depositors = Depositor.query.all()
    result = []

    for depositor in depositors:
        result.append(get_depositor_report(depositor.id))

    return result
