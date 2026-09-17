from datetime import date
from decimal import Decimal, InvalidOperation

from repositories import deposit_repository, depositor_repository, currency_repository

PAGE_SIZES = [10, 25, 50]
STATUSES = ["Active", "Pending", "Closed", "Blocked"]


def months_between(start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    if end_date.day < start_date.day:
        months = months - 1
    return months


def term_months(start_date, end_date):
    months = months_between(start_date, end_date)
    if months < 0:
        return 0
    return months


def serialize(deposit, today):
    term = term_months(deposit.start_date, deposit.end_date)
    amount = float(deposit.amount)
    interest_rate = float(deposit.interest_rate)
    term_end_accruals = round(amount * interest_rate / 100 * term / 12, 2)
    amount_to_be_paid = round(amount + term_end_accruals, 2)
    elapsed = months_between(deposit.start_date, today)
    if elapsed < 0:
        elapsed = 0
    if elapsed > term:
        elapsed = term
    accrued = 0.0
    if term > 0:
        accrued = round(term_end_accruals * elapsed / term, 2)
    return {
        "id": deposit.id,
        "deposit_number": "D-" + str(deposit.ordinal).zfill(4),
        "depositor_id": deposit.depositor_id,
        "depositor": deposit.depositor_name,
        "status": deposit.status,
        "currency_id": deposit.currency_id,
        "currency": deposit.currency,
        "amount": amount,
        "interest_rate": interest_rate,
        "start_date": deposit.start_date.isoformat(),
        "end_date": deposit.end_date.isoformat(),
        "term_months": term,
        "term_end_accruals": term_end_accruals,
        "amount_to_be_paid": amount_to_be_paid,
        "accrued": accrued,
        "opened": deposit.created_at.date().isoformat(),
    }


def validate(connection, payload):
    try:
        payload["depositor_id"] = int(payload["depositor_id"])
    except (TypeError, ValueError):
        return "depositor is invalid"
    if not depositor_repository.get_depositor(connection, payload["depositor_id"]):
        return "depositor is invalid"
    try:
        payload["currency_id"] = int(payload["currency_id"])
    except (TypeError, ValueError):
        return "currency is invalid"
    if not currency_repository.currency_exists(connection, payload["currency_id"]):
        return "currency is invalid"
    if payload["status"] not in STATUSES:
        return "status is invalid"
    try:
        payload["amount"] = Decimal(payload["amount"])
    except (TypeError, ValueError, InvalidOperation):
        return "amount is invalid"
    if payload["amount"] <= 0:
        return "amount must be greater than zero"
    try:
        payload["interest_rate"] = Decimal(payload["interest_rate"])
    except (TypeError, ValueError, InvalidOperation):
        return "interest rate is invalid"
    if payload["interest_rate"] < 0:
        return "interest rate is invalid"
    try:
        payload["start_date"] = date.fromisoformat(payload["start_date"])
    except ValueError:
        return "start date is invalid"
    try:
        payload["end_date"] = date.fromisoformat(payload["end_date"])
    except ValueError:
        return "end date is invalid"
    if payload["end_date"] <= payload["start_date"]:
        return "end date must be after the start date"
    return None


def list_deposits(connection, search, sort, order, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    total = deposit_repository.count_deposits(connection, search)
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    deposits = deposit_repository.list_deposits(connection, search, sort, order, page_size, offset)
    today = date.today()
    items = [serialize(deposit, today) for deposit in deposits]
    return {"deposits": items, "total": total, "page": page, "pages": pages, "page_size": page_size}, 200


def get_stats(connection):
    counts = deposit_repository.count_by_status(connection)
    active = counts.get("Active", 0)
    pending = counts.get("Pending", 0)
    closed = counts.get("Closed", 0)
    blocked = counts.get("Blocked", 0)
    total = sum(counts.values())
    currency_counts = deposit_repository.count_by_currency(connection)
    usd = currency_counts.get("USD", 0)
    eur = currency_counts.get("EUR", 0)
    rub = currency_counts.get("RUB", 0)
    amount_counts = deposit_repository.sum_by_currency(connection)
    amount_usd = amount_counts.get("USD", 0.0)
    amount_eur = amount_counts.get("EUR", 0.0)
    amount_rub = amount_counts.get("RUB", 0.0)
    amount_total = round(amount_usd + amount_eur + amount_rub, 2)
    next_number = "D-" + str(total + 1).zfill(4)
    return {
        "total": total,
        "active": active,
        "next_number": next_number,
        "statuses": {"total": total, "active": active, "pending": pending, "closed": closed, "blocked": blocked},
        "currencies": {"total": total, "usd": usd, "eur": eur, "rub": rub},
        "amounts": {"total": amount_total, "usd": amount_usd, "eur": amount_eur, "rub": amount_rub},
    }, 200


def get_deposit(connection, deposit_id):
    deposit = deposit_repository.get_deposit(connection, deposit_id)
    if not deposit:
        return {"error": "deposit not found"}, 404
    return serialize(deposit, date.today()), 200


def create_deposit(connection, payload, user_id):
    error = validate(connection, payload)
    if error:
        return {"error": error}, 400
    deposit = deposit_repository.create_deposit(connection, payload, user_id)
    return serialize(deposit, date.today()), 201


def update_deposit(connection, deposit_id, payload):
    error = validate(connection, payload)
    if error:
        return {"error": error}, 400
    deposit = deposit_repository.update_deposit(connection, deposit_id, payload)
    if not deposit:
        return {"error": "deposit not found"}, 404
    return serialize(deposit, date.today()), 200


def delete_deposit(connection, deposit_id):
    deposit = deposit_repository.get_deposit(connection, deposit_id)
    if not deposit:
        return {"error": "deposit not found"}, 404
    deposit_repository.delete_deposit(connection, deposit_id)
    return {"deleted": True}, 200
