import psycopg
from fastapi import HTTPException

import database


def get_connection():
    try:
        connection = database.connect()
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail={"error": "database unavailable", "fallback": True})
    try:
        yield connection
    finally:
        connection.close()
