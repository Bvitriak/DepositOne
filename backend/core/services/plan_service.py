import calendar
from datetime import date, timedelta

from repositories import plan_repository
from services import deposit_service

PAGE_SIZES = [10, 25, 50]
PRIORITY_SIZE = 4
WEEK_DAYS = 6


def add_months(start_date, months):
    index = start_date.month - 1 + months
    year = start_date.year + index // 12
    month = index % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def month_bounds(today):
    first_day = date(today.year, today.month, 1)
    if today.month == 12:
        last_day = date(today.year, 12, 31)
    else:
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return first_day, last_day


def build_amounts(plan, today):
    term = deposit_service.term_months(plan.start_date, plan.end_date)
    amount = float(plan.amount)
    interest_rate = float(plan.interest_rate)
    term_end_accruals = round(amount * interest_rate / 100 * term / 12, 2)
    elapsed = deposit_service.months_between(plan.start_date, today)
    if elapsed < 0:
        elapsed = 0
    if elapsed > term:
        elapsed = term
    accrued = 0.0
    if term > 0:
        accrued = round(term_end_accruals * elapsed / term, 2)
    return {
        "amount": amount,
        "interest_rate": interest_rate,
        "term_months": term,
        "term_end_accruals": term_end_accruals,
        "accrued": accrued,
        "total_refund": round(amount + term_end_accruals, 2),
    }


def build_contract_number(plan):
    if not plan.contract_ordinal:
        return None
    return "K-" + str(plan.contract_ordinal).zfill(4)


def serialize(plan, today):
    amounts = build_amounts(plan, today)
    return {
        "deposit_id": plan.deposit_id,
        "deposit_number": "D-" + str(plan.ordinal).zfill(4),
        "contract_number": build_contract_number(plan),
        "depositor_id": plan.depositor_id,
        "depositor": plan.depositor_name,
        "phone": plan.phone,
        "email": plan.email,
        "currency": plan.currency,
        "amount": amounts["amount"],
        "interest_rate": amounts["interest_rate"],
        "term_months": amounts["term_months"],
        "term_end_accruals": amounts["term_end_accruals"],
        "accrued": amounts["accrued"],
        "total_refund": amounts["total_refund"],
        "start_date": plan.start_date.isoformat(),
        "payout_date": plan.end_date.isoformat(),
    }


def build_priority(plan, today):
    amounts = build_amounts(plan, today)
    return {
        "deposit_id": plan.deposit_id,
        "deposit_number": "D-" + str(plan.ordinal).zfill(4),
        "depositor": plan.depositor_name,
        "currency": plan.currency,
        "interest_rate": amounts["interest_rate"],
        "total_refund": amounts["total_refund"],
        "days_left": (plan.end_date - today).days,
    }


def build_accrual_history(plan, today):
    amounts = build_amounts(plan, today)
    term = amounts["term_months"]
    amount = amounts["amount"]
    if term == 0:
        return [{
            "number": 1,
            "date": plan.end_date.isoformat(),
            "accrued": 0.0,
            "capitalization": False,
            "total": round(amount, 2),
        }]
    monthly = amounts["term_end_accruals"] / term
    rows = []
    for number in range(1, term + 1):
        row_date = plan.end_date
        if number < term:
            row_date = add_months(plan.start_date, number)
        rows.append({
            "number": number,
            "date": row_date.isoformat(),
            "accrued": round(monthly, 2),
            "capitalization": number < term,
            "total": round(amount + monthly * number, 2),
        })
    return rows


def list_plans(connection, search, sort, order, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    total = plan_repository.count_plans(connection, search)
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    plans = plan_repository.list_plans(connection, search, sort, order, page_size, offset)
    today = date.today()
    items = [serialize(plan, today) for plan in plans]
    return {"plans": items, "total": total, "page": page, "pages": pages, "page_size": page_size}, 200


def get_summary(connection):
    today = date.today()
    first_day, last_day = month_bounds(today)
    amount, returns = plan_repository.get_month_totals(connection, first_day, last_day)
    tomorrow = today + timedelta(days=1)
    week_end = today + timedelta(days=WEEK_DAYS)
    reserve = None
    if amount > 0:
        reserve = round(plan_repository.get_reserve_amount(connection, last_day) / amount * 100)
    plans = plan_repository.list_priority(connection, today, PRIORITY_SIZE)
    monthly = {
        "amount": round(amount, 2),
        "returns": returns,
        "reserve": reserve,
        "tomorrow": plan_repository.count_returns(connection, tomorrow, tomorrow),
        "this_week": plan_repository.count_returns(connection, today, week_end),
    }
    priority = [build_priority(plan, today) for plan in plans]
    return {"monthly": monthly, "priority": priority}, 200


def get_plan(connection, deposit_id):
    plan = plan_repository.get_plan(connection, deposit_id)
    if not plan:
        return {"error": "return plan not found"}, 404
    today = date.today()
    item = serialize(plan, today)
    item["accruals"] = build_accrual_history(plan, today)
    return item, 200
