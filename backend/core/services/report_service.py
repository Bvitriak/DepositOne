from datetime import date, timedelta

from repositories import report_repository

PAGE_SIZES = [10, 25, 50]


def serialize(report):
    return {
        "depositor_id": report.depositor_id,
        "depositor": report.depositor_name,
        "deposits": report.deposits,
        "total_amount": round(float(report.total_amount), 2),
        "total_income": round(float(report.total_income), 2),
    }


def month_end(today):
    if today.month == 12:
        return date(today.year, 12, 31)
    return date(today.year, today.month + 1, 1) - timedelta(days=1)


def build_periods(today):
    return [
        {"name": "Today", "end": today},
        {"name": "Month", "end": month_end(today)},
        {"name": "Year", "end": date(today.year, 12, 31)},
        {"name": "5 Years", "end": date(today.year + 4, 12, 31)},
    ]


def list_reports(connection, search, sort, order, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    total = report_repository.count_reports(connection, search)
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    reports = report_repository.list_reports(connection, search, sort, order, page_size, offset)
    items = [serialize(report) for report in reports]
    return {"reports": items, "total": total, "page": page, "pages": pages, "page_size": page_size}, 200


def get_cash_flow(connection):
    cards = []
    for period in build_periods(date.today()):
        inflow, outflow = report_repository.get_cash_flow(connection, period["end"])
        cards.append({
            "period": period["name"],
            "inflow": round(inflow, 2),
            "outflow": round(outflow, 2),
            "net": round(inflow - outflow, 2),
        })
    return {"cash_flow": cards}, 200
