from datetime import date
from decimal import Decimal, InvalidOperation

from repositories import deposit_repository, depositor_repository, currency_repository, contract_repository
from utils import currency

PAGE_SIZES = [10, 25, 50]
DAYS_IN_YEAR = 365
MAX_AMOUNT = Decimal("9999999999999.99")
MAX_INTEREST_RATE = Decimal("100")
ACTIVE_STATUS = "Active"
STATUSES = [ACTIVE_STATUS, "Pending", "Closed", "Blocked"]


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


def term_days(start_date, end_date):
    days = (end_date - start_date).days
    if days < 0:
        return 0
    return days


def interest(amount, interest_rate, days):
    return round(amount * interest_rate / 100 * days / DAYS_IN_YEAR, 2)


def serialize(deposit, today):
    term = term_months(deposit.start_date, deposit.end_date)
    days = term_days(deposit.start_date, deposit.end_date)
    amount = float(deposit.amount)
    interest_rate = float(deposit.interest_rate)
    term_end_accruals = interest(amount, interest_rate, days)
    amount_to_be_paid = round(amount + term_end_accruals, 2)
    accrued = 0.0
    if deposit.status == ACTIVE_STATUS:
        elapsed = min(max(term_days(deposit.start_date, today), 0), days)
        accrued = interest(amount, interest_rate, elapsed)
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
    if not payload["amount"].is_finite():
        return "amount is invalid"
    if payload["amount"] <= 0:
        return "amount must be greater than zero"
    if payload["amount"] > MAX_AMOUNT:
        return "amount must not exceed " + str(MAX_AMOUNT)
    try:
        payload["interest_rate"] = Decimal(payload["interest_rate"])
    except (TypeError, ValueError, InvalidOperation):
        return "interest rate is invalid"
    if not payload["interest_rate"].is_finite():
        return "interest rate is invalid"
    if payload["interest_rate"] < 0 or payload["interest_rate"] > MAX_INTEREST_RATE:
        return "interest rate must be between 0 and " + str(MAX_INTEREST_RATE)
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


def list_options(connection):
    rows = deposit_repository.list_options(connection)
    options = []
    for row in rows:
        amount = float(row["amount"])
        interest_rate = float(row["interest_rate"])
        term_end_accruals = interest(amount, interest_rate, term_days(row["start_date"], row["end_date"]))
        options.append({
            "id": row["id"],
            "number": "D-" + str(row["ordinal"]).zfill(4),
            "depositor_id": row["depositor_id"],
            "depositor": row["depositor_name"],
            "currency": row["code"],
            "amount": amount,
            "interest_rate": interest_rate,
            "term_end_accruals": term_end_accruals,
            "start_date": row["start_date"].isoformat(),
            "end_date": row["end_date"].isoformat(),
        })
    return {"deposits": options}, 200


def get_stats(connection, code):
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
    amount_usd = currency.convert(amount_counts.get("USD", 0.0), code)
    amount_eur = currency.convert(amount_counts.get("EUR", 0.0), code)
    amount_rub = currency.convert(amount_counts.get("RUB", 0.0), code)
    amount_total = round(amount_usd + amount_eur + amount_rub, 2)
    accrued = currency.convert(deposit_repository.sum_accrued(connection, date.today()), code)
    next_number = "D-" + str(total + 1).zfill(4)
    return {
        "total": total,
        "active": active,
        "next_number": next_number,
        "statuses": {"total": total, "active": active, "pending": pending, "closed": closed, "blocked": blocked},
        "currencies": {"total": total, "usd": usd, "eur": eur, "rub": rub},
        "amounts": {"total": amount_total, "usd": amount_usd, "eur": amount_eur, "rub": amount_rub},
        "accrued": accrued,
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
    if contract_repository.count_by_deposit(connection, deposit_id, 0) > 0:
        return {"error": "deposit has a contract", "deletable": False}, 409
    deposit_repository.delete_deposit(connection, deposit_id)
    return {"deleted": True}, 200
