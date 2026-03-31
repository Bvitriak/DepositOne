from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from app.db import db
from app.models.deposit import Deposit
from app.models.interestAccrual import InterestAccrual

TWO_PLACES = Decimal("0.01")
DAYS_IN_YEAR = Decimal("365")

def to_decimal(value):
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def calculate_days(start_date, end_date):
    return (end_date - start_date).days

def calculate_interest(amount, annual_rate, days):
    amount = Decimal(str(amount))
    annual_rate = Decimal(str(annual_rate))
    days = Decimal(str(days))

    interest = amount * (annual_rate / Decimal("100")) * (days / DAYS_IN_YEAR)
    return interest.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def calculate_total_amount(amount, interest_amount):
    total = Decimal(str(amount)) + Decimal(str(interest_amount))
    return total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def calculate_deposit_return(deposit: Deposit):
    days = calculate_days(deposit.start_date, deposit.end_date)
    interest_amount = calculate_interest(deposit.amount, deposit.interest_rate, days)
    total_amount = calculate_total_amount(deposit.amount, interest_amount)

    return {
        "deposit_id": deposit.id,
        "days": days,
        "interest_amount": interest_amount,
        "total_amount": total_amount
    }

def create_accrual_for_deposit(deposit: Deposit):
    existing = InterestAccrual.query.filter_by(
        deposit_id=deposit.id,
        period_start=deposit.start_date,
        period_end=deposit.end_date
    ).first()

    if existing:
        return existing

    result = calculate_deposit_return(deposit)

    accrual = InterestAccrual(
        deposit_id=deposit.id,
        accrual_date=date.today(),
        period_start=deposit.start_date,
        period_end=deposit.end_date,
        interest_amount=result["interest_amount"],
        total_amount=result["total_amount"],
        is_paid=False
    )

    db.session.add(accrual)
    db.session.commit()

    return accrual

def get_deposits_for_return_tomorrow():
    tomorrow = date.today().fromordinal(date.today().toordinal() + 1)

    deposits = Deposit.query.filter(
        Deposit.end_date == tomorrow,
        Deposit.status == "active"
    ).all()

    result = []
    for deposit in deposits:
        result.append(calculate_deposit_return(deposit))

    return result

def get_month_return_plan(year, month):
    deposits = Deposit.query.filter(
        db.extract("year", Deposit.end_date) == year,
        db.extract("month", Deposit.end_date) == month,
        Deposit.status == "active"
    ).all()

    plan = []
    total_sum = Decimal("0.00")

    for deposit in deposits:
        data = calculate_deposit_return(deposit)
        plan.append(data)
        total_sum += data["total_amount"]

    return {
        "items": plan,
        "total_sum": total_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    }
