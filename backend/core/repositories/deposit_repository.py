from models.deposit import Deposit

SORT_COLUMNS = {
    "created": "d.created_at",
    "name": "dep.last_name",
    "amount": "d.amount",
    "rate": "d.interest_rate",
    "end": "d.end_date",
}

ORDINAL = "(SELECT count(*) FROM deposits dd WHERE dd.id <= d.id)"

SEARCH_CONDITION = (
    "(dep.first_name || ' ' || dep.last_name) ILIKE %s "
    "OR ('D-' || lpad(" + ORDINAL + "::text, 4, '0')) ILIKE %s "
    "OR d.status ILIKE %s "
    "OR c.code ILIKE %s "
    "OR CAST(d.amount AS TEXT) ILIKE %s"
)

SELECT_COLUMNS = (
    "d.id, d.depositor_id, dep.first_name, dep.last_name, d.currency_id, c.code, "
    "d.status, d.amount, d.interest_rate, d.start_date, d.end_date, d.created_at, "
    + ORDINAL + " AS ordinal"
)

FROM_JOIN = (
    "FROM deposits d "
    "JOIN depositors dep ON dep.id = d.depositor_id "
    "JOIN currencies c ON c.id = d.currency_id "
)


def build_row(row):
    return Deposit(
        id=row[0],
        depositor_id=row[1],
        depositor_name=row[2] + " " + row[3],
        currency_id=row[4],
        currency=row[5],
        status=row[6],
        amount=row[7],
        interest_rate=row[8],
        start_date=row[9],
        end_date=row[10],
        created_at=row[11],
        ordinal=row[12],
    )


def list_deposits(connection, search, sort, order, limit, offset):
    column = SORT_COLUMNS.get(sort, SORT_COLUMNS["created"])
    direction = "ASC" if order == "asc" else "DESC"
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like]
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


def count_deposits(connection, search):
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like]
    query = "SELECT count(*) " + FROM_JOIN + where
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        total = cursor.fetchone()[0]
    return total


def count_by_status(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT status, count(*) FROM deposits GROUP BY status")
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}


def count_by_currency(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT c.code, count(*) FROM deposits d "
            "JOIN currencies c ON c.id = d.currency_id GROUP BY c.code"
        )
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}


def sum_by_currency(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT c.code, COALESCE(sum(d.amount), 0) FROM deposits d "
            "JOIN currencies c ON c.id = d.currency_id GROUP BY c.code"
        )
        rows = cursor.fetchall()
    return {row[0]: float(row[1]) for row in rows}


def list_options(connection):
    query = (
        "SELECT d.id, " + ORDINAL + " AS ordinal, d.depositor_id, dep.first_name, dep.last_name, "
        "c.code, d.amount, d.interest_rate, d.start_date, d.end_date "
        "FROM deposits d "
        "JOIN depositors dep ON dep.id = d.depositor_id "
        "JOIN currencies c ON c.id = d.currency_id ORDER BY d.id ASC"
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "ordinal": row[1],
            "depositor_id": row[2],
            "depositor_name": row[3] + " " + row[4],
            "code": row[5],
            "amount": row[6],
            "interest_rate": row[7],
            "start_date": row[8],
            "end_date": row[9],
        }
        for row in rows
    ]


def count_active_by_depositor(connection, depositor_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM deposits WHERE depositor_id = %s AND status = 'Active'",
            (depositor_id,),
        )
        total = cursor.fetchone()[0]
    return total


def get_deposit(connection, deposit_id):
    query = "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN + "WHERE d.id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (deposit_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return build_row(row)


def create_deposit(connection, data, created_by):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO deposits "
            "(depositor_id, currency_id, status, amount, interest_rate, start_date, end_date, created_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                data["depositor_id"],
                data["currency_id"],
                data["status"],
                data["amount"],
                data["interest_rate"],
                data["start_date"],
                data["end_date"],
                created_by,
            ),
        )
        deposit_id = cursor.fetchone()[0]
        connection.commit()
    return get_deposit(connection, deposit_id)


def update_deposit(connection, deposit_id, data):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE deposits SET depositor_id = %s, currency_id = %s, status = %s, "
            "amount = %s, interest_rate = %s, start_date = %s, end_date = %s WHERE id = %s",
            (
                data["depositor_id"],
                data["currency_id"],
                data["status"],
                data["amount"],
                data["interest_rate"],
                data["start_date"],
                data["end_date"],
                deposit_id,
            ),
        )
        updated = cursor.rowcount
        connection.commit()
    if not updated:
        return None
    return get_deposit(connection, deposit_id)


def delete_deposit(connection, deposit_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM deposits WHERE id = %s", (deposit_id,))
        deleted = cursor.rowcount
        connection.commit()
    return deleted
