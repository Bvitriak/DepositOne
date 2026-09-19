from models.plan import Plan
from utils import currency

AMOUNT = currency.in_rubles("d.amount", "c.code")

ACTIVE = "d.status = 'Active'"

SORT_COLUMNS = {
    "payout": "d.end_date",
    "amount": AMOUNT,
    "rate": "d.interest_rate",
    "name": "dep.last_name",
}

DEPOSIT_ORDINAL = "(SELECT count(*) FROM deposits x WHERE x.id <= d.id)"

CONTRACT_ORDINAL = (
    "(SELECT count(*) FROM contracts y WHERE y.id <= "
    "(SELECT min(z.id) FROM contracts z WHERE z.deposit_id = d.id))"
)

DEPOSIT_NUMBER = "('D-' || lpad(" + DEPOSIT_ORDINAL + "::text, 4, '0'))"

TERM_DAYS = "(d.end_date - d.start_date)"

TOTAL_REFUND = "(" + AMOUNT + " + " + AMOUNT + " * d.interest_rate / 100 * " + TERM_DAYS + " / 365)"

SEARCH_CONDITION = (
    DEPOSIT_NUMBER + " ILIKE %s "
    "OR (dep.first_name || ' ' || dep.last_name) ILIKE %s "
    "OR c.code ILIKE %s "
    "OR to_char(d.end_date, 'DD.MM.YYYY') ILIKE %s"
)

SELECT_COLUMNS = (
    "d.id, " + DEPOSIT_ORDINAL + " AS ordinal, " + CONTRACT_ORDINAL + " AS contract_ordinal, "
    "d.depositor_id, dep.first_name, dep.last_name, dep.phone, dep.email, "
    "c.code, d.amount, d.interest_rate, d.start_date, d.end_date"
)

FROM_JOIN = (
    "FROM deposits d "
    "JOIN depositors dep ON dep.id = d.depositor_id "
    "JOIN currencies c ON c.id = d.currency_id "
)


def build_row(row):
    return Plan(
        deposit_id=row[0],
        ordinal=row[1],
        contract_ordinal=row[2],
        depositor_id=row[3],
        depositor_name=row[4] + " " + row[5],
        phone=row[6],
        email=row[7],
        currency=row[8],
        amount=row[9],
        interest_rate=row[10],
        start_date=row[11],
        end_date=row[12],
    )


def list_plans(connection, search, sort, order, limit, offset):
    column = SORT_COLUMNS.get(sort, SORT_COLUMNS["payout"])
    direction = "DESC" if order == "desc" else "ASC"
    where = "WHERE " + ACTIVE
    parameters = []
    if search:
        where = where + " AND (" + SEARCH_CONDITION + ")"
        like = "%" + search + "%"
        parameters = [like, like, like, like]
    query = (
        "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN
        + where +
        " ORDER BY " + column + " " + direction + " LIMIT %s OFFSET %s"
    )
    parameters = parameters + [limit, offset]
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
    return [build_row(row) for row in rows]


def count_plans(connection, search):
    where = "WHERE " + ACTIVE
    parameters = []
    if search:
        where = where + " AND (" + SEARCH_CONDITION + ")"
        like = "%" + search + "%"
        parameters = [like, like, like, like]
    query = "SELECT count(*) " + FROM_JOIN + where
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        total = cursor.fetchone()[0]
    return total


def get_plan(connection, deposit_id):
    query = "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN + "WHERE d.id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (deposit_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return build_row(row)


def list_priority(connection, today, limit):
    query = (
        "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN +
        "WHERE " + ACTIVE + " AND d.end_date >= %s ORDER BY d.end_date ASC LIMIT %s"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (today, limit))
        rows = cursor.fetchall()
    return [build_row(row) for row in rows]


def get_month_totals(connection, first_day, last_day):
    query = (
        "SELECT COALESCE(sum(" + TOTAL_REFUND + "), 0), count(d.id) "
        "FROM deposits d JOIN currencies c ON c.id = d.currency_id "
        "WHERE " + ACTIVE + " AND d.end_date BETWEEN %s AND %s"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (first_day, last_day))
        row = cursor.fetchone()
    return float(row[0]), row[1]


def count_returns(connection, first_day, last_day):
    query = "SELECT count(d.id) FROM deposits d WHERE " + ACTIVE + " AND d.end_date BETWEEN %s AND %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (first_day, last_day))
        total = cursor.fetchone()[0]
    return total


def get_reserve_amount(connection, last_day):
    query = (
        "SELECT COALESCE(sum(" + AMOUNT + "), 0) FROM deposits d "
        "JOIN currencies c ON c.id = d.currency_id WHERE " + ACTIVE + " AND d.end_date > %s"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (last_day,))
        total = cursor.fetchone()[0]
    return float(total)
