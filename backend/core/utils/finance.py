DAYS_IN_YEAR = 365


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
