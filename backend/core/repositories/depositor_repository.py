from models.depositor import Depositor

SORT_COLUMNS = {
    "created": "d.created_at",
    "name": "d.last_name",
    "country": "c.name",
    "dob": "d.date_of_birth",
}

SEARCH_CONDITION = (
    "(d.first_name || ' ' || d.last_name) ILIKE %s "
    "OR to_char(d.date_of_birth, 'DD.MM.YYYY') ILIKE %s "
    "OR d.email ILIKE %s "
    "OR c.name ILIKE %s "
    "OR d.address ILIKE %s"
)

SELECT_COLUMNS = (
    "d.id, d.first_name, d.last_name, d.date_of_birth, d.country_id, c.name, "
    "d.passport, d.tin, d.phone, d.email, d.address, d.created_at"
)


def build_row(row):
    return Depositor(
        id=row[0],
        first_name=row[1],
        last_name=row[2],
        date_of_birth=row[3],
        country_id=row[4],
        country=row[5],
        passport=row[6],
        tin=row[7],
        phone=row[8],
        email=row[9],
        address=row[10],
        created_at=row[11],
    )


def list_depositors(connection, search, sort, order, limit, offset):
    column = SORT_COLUMNS.get(sort, SORT_COLUMNS["created"])
    direction = "ASC" if order == "asc" else "DESC"
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like]
    query = (
        "SELECT " + SELECT_COLUMNS + " FROM depositors d "
        "JOIN countries c ON c.id = d.country_id "
        + where +
        " ORDER BY " + column + " " + direction + " LIMIT %s OFFSET %s"
    )
    parameters = parameters + [limit, offset]
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
    return [build_row(row) for row in rows]


def count_depositors(connection, search):
    where = ""
    parameters = []
    if search:
        where = "WHERE " + SEARCH_CONDITION
        like = "%" + search + "%"
        parameters = [like, like, like, like, like]
    query = (
        "SELECT count(*) FROM depositors d "
        "JOIN countries c ON c.id = d.country_id " + where
    )
    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        total = cursor.fetchone()[0]
    return total


def get_depositor(connection, depositor_id):
    query = (
        "SELECT " + SELECT_COLUMNS + " FROM depositors d "
        "JOIN countries c ON c.id = d.country_id WHERE d.id = %s"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (depositor_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return build_row(row)


def create_depositor(connection, data, created_by):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO depositors "
            "(first_name, last_name, date_of_birth, country_id, passport, tin, phone, email, address, created_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (
                data["first_name"],
                data["last_name"],
                data["date_of_birth"],
                data["country_id"],
                data["passport"],
                data["tin"],
                data["phone"],
                data["email"],
                data["address"],
                created_by,
            ),
        )
        depositor_id = cursor.fetchone()[0]
        connection.commit()
    return get_depositor(connection, depositor_id)


def update_depositor(connection, depositor_id, data):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE depositors SET first_name = %s, last_name = %s, date_of_birth = %s, "
            "country_id = %s, passport = %s, tin = %s, phone = %s, email = %s, address = %s "
            "WHERE id = %s",
            (
                data["first_name"],
                data["last_name"],
                data["date_of_birth"],
                data["country_id"],
                data["passport"],
                data["tin"],
                data["phone"],
                data["email"],
                data["address"],
                depositor_id,
            ),
        )
        updated = cursor.rowcount
        connection.commit()
    if not updated:
        return None
    return get_depositor(connection, depositor_id)


def delete_depositor(connection, depositor_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM depositors WHERE id = %s", (depositor_id,))
        deleted = cursor.rowcount
        connection.commit()
    return deleted
