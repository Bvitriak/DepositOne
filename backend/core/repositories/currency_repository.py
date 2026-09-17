def list_currencies(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, code FROM currencies ORDER BY code ASC")
        rows = cursor.fetchall()
    return [{"id": row[0], "code": row[1]} for row in rows]


def currency_exists(connection, currency_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM currencies WHERE id = %s", (currency_id,))
        row = cursor.fetchone()
    return row is not None
