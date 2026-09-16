import os
import psycopg


def connect():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=os.getenv("DATABASE_PORT", "5432"),
        dbname=os.getenv("DATABASE_NAME", "depositone"),
        user=os.getenv("DATABASE_USER", "depositone"),
        password=os.getenv("DATABASE_PASSWORD", "depositone"),
    )
