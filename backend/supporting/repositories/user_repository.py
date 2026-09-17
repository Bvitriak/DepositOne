from models.user import User


def create(connection, username, email, password_hash):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id, username",
            (username, email, password_hash),
        )
        row = cursor.fetchone()
        connection.commit()
    return User(id=row[0], username=row[1])


def count(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM users")
        total = cursor.fetchone()[0]
    return total


def find_by_email(connection, email):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE email = %s",
            (email,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    return User(id=row[0], username=row[1], email=row[2], password_hash=row[3])


def update_password(connection, email, password_hash):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (password_hash, email),
        )
        updated = cursor.rowcount
        connection.commit()
    return updated
