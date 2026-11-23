def get_overview(connection):
    return {
        "summary": {
            "depositors": None,
            "deposits": None,
            "active": None,
            "portfolio": None,
            "percents": None,
        },
        "statuses": {
            "total": None,
            "active": None,
            "pending": None,
            "closed": None,
            "blocked": None,
        },
        "currencies": {
            "total": None,
            "usd": None,
            "eur": None,
            "rub": None,
        },
        "depositors": [],
    }
