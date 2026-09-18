from models.report import Report

TERM_DAYS = "(d.end_date - d.start_date)"

INCOME = "(d.amount * d.interest_rate / 100 * " + TERM_DAYS + " / 365)"

SORT_COLUMNS = {
    "amount": "sum(d.amount)",
    "income": "sum(" + INCOME + ")",
    "deposits": "count(d.id)",
    "name": "dep.last_name",
}

SEARCH_CONDITION = "(dep.first_name || ' ' || dep.last_name) ILIKE %s"

SELECT_COLUMNS = (
    "dep.id, dep.first_name, dep.last_name, count(d.id), "
    "COALESCE(sum(d.amount), 0), COALESCE(sum(" + INCOME + "), 0)"
)

FROM_JOIN = "FROM depositors dep JOIN deposits d ON d.depositor_id = dep.id "

GROUP_BY = " GROUP BY dep.id, dep.first_name, dep.last_name"


def build_row(row):
    return Report(
        depositor_id=row[0],
        depositor_name=row[1] + " " + row[2],
        deposits=row[3],
        total_amount=row[4],
        total_income=row[5],
    )


def list_reports(connection, search, sort, order, limit, offset):
    column = SORT_COLUMNS.get(sort, SORT_COLUMNS["amount"])
    direction = "ASC" if order == "asc" else "DESC"
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        parameters = ["%" + search + "%"]
    query = (
        "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN
        + where + GROUP_BY +
        " ORDER BY " + column + " " + direction + " LIMIT %s OFFSET %s"
    )
    parameters = parameters + [limit, offset]
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
    return [build_row(row) for row in rows]


def count_reports(connection, search):
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        parameters = ["%" + search + "%"]
    query = "SELECT count(DISTINCT dep.id) " + FROM_JOIN + where
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        total = cursor.fetchone()[0]
    return total


def get_cash_flow(connection, end_date):
    query = (
        "SELECT "
        "COALESCE(sum(d.amount) FILTER (WHERE d.start_date <= %s), 0), "
        "COALESCE(sum(d.amount + " + INCOME + ") FILTER (WHERE d.end_date <= %s), 0) "
        "FROM deposits d"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (end_date, end_date))
        row = cursor.fetchone()
    return float(row[0]), float(row[1])
