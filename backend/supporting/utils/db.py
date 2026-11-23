from functools import wraps

import psycopg
from flask import jsonify

import database


def with_db(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            connection = database.connect()
        except psycopg.OperationalError:
            return jsonify(error="database unavailable", fallback=True), 503
        try:
            return view(connection, *args, **kwargs)
        finally:
            connection.close()
    return wrapper
