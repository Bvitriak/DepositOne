from models.contract import Contract

SORT_COLUMNS = {
    "created": "ct.created_at",
    "date": "ct.contract_date",
    "name": "dep.last_name",
    "status": "ct.signing_status",
}

CONTRACT_ORDINAL = "(SELECT count(*) FROM contracts x WHERE x.id <= ct.id)"
DEPOSIT_ORDINAL = "(SELECT count(*) FROM deposits y WHERE y.id <= d.id)"

DEPOSIT_NUMBER = "('D-' || lpad(" + DEPOSIT_ORDINAL + "::text, 4, '0'))"
CONTRACT_CODE = "('K-' || lpad(" + CONTRACT_ORDINAL + "::text, 4, '0'))"
CONTRACT_NUMBER = "(to_char(ct.contract_date, 'YYYY/MM') || '/' || " + DEPOSIT_NUMBER + ")"

SEARCH_CONDITION = (
    CONTRACT_CODE + " ILIKE %s "
    "OR " + CONTRACT_NUMBER + " ILIKE %s "
    "OR " + DEPOSIT_NUMBER + " ILIKE %s "
    "OR (dep.first_name || ' ' || dep.last_name) ILIKE %s "
    "OR ct.signing_status ILIKE %s "
    "OR to_char(ct.contract_date, 'DD.MM.YYYY') ILIKE %s"
)

SELECT_COLUMNS = (
    "ct.id, " + CONTRACT_ORDINAL + " AS ordinal, ct.deposit_id, " + DEPOSIT_ORDINAL + " AS deposit_ordinal, "
    "d.depositor_id, dep.first_name, dep.last_name, cur.code, d.amount, d.interest_rate, "
    "d.start_date, d.end_date, ct.contract_date, ct.signing_status, ct.description, "
    "ct.special_conditions, ct.created_at"
)

FROM_JOIN = (
    "FROM contracts ct "
    "JOIN deposits d ON d.id = ct.deposit_id "
    "JOIN depositors dep ON dep.id = d.depositor_id "
    "JOIN currencies cur ON cur.id = d.currency_id "
)


def build_row(row):
    return Contract(
        id=row[0],
        ordinal=row[1],
        deposit_id=row[2],
        deposit_ordinal=row[3],
        depositor_id=row[4],
        depositor_name=row[5] + " " + row[6],
        currency=row[7],
        amount=row[8],
        interest_rate=row[9],
        start_date=row[10],
        end_date=row[11],
        contract_date=row[12],
        signing_status=row[13],
        description=row[14],
        special_conditions=row[15],
        created_at=row[16],
    )


def list_contracts(connection, search, sort, order, limit, offset):
    column = SORT_COLUMNS.get(sort, SORT_COLUMNS["created"])
    direction = "ASC" if order == "asc" else "DESC"
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like, like]
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


def count_contracts(connection, search):
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like, like]
    query = "SELECT count(*) " + FROM_JOIN + where
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        total = cursor.fetchone()[0]
    return total


def get_contract(connection, contract_id):
    query = "SELECT " + SELECT_COLUMNS + " " + FROM_JOIN + "WHERE ct.id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (contract_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return build_row(row)


def create_contract(connection, data, created_by):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO contracts "
            "(deposit_id, contract_date, signing_status, description, special_conditions, created_by) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (
                data["deposit_id"],
                data["contract_date"],
                data["signing_status"],
                data["description"],
                data["special_conditions"],
                created_by,
            ),
        )
        contract_id = cursor.fetchone()[0]
        connection.commit()
    return get_contract(connection, contract_id)


def update_contract(connection, contract_id, data):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE contracts SET deposit_id = %s, contract_date = %s, signing_status = %s, "
            "description = %s, special_conditions = %s WHERE id = %s",
            (
                data["deposit_id"],
                data["contract_date"],
                data["signing_status"],
                data["description"],
                data["special_conditions"],
                contract_id,
            ),
        )
        updated = cursor.rowcount
        connection.commit()
    if not updated:
        return None
    return get_contract(connection, contract_id)


def delete_contract(connection, contract_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM contracts WHERE id = %s", (contract_id,))
        deleted = cursor.rowcount
        connection.commit()
    return deleted
