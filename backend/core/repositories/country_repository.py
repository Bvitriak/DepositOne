def list_countries(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM countries ORDER BY name ASC")
        rows = cursor.fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]


def country_exists(connection, country_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM countries WHERE id = %s", (country_id,))
        row = cursor.fetchone()
    return row is not None
