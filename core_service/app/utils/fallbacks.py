import sqlite3

ERROR_DB_UNAVAILABLE = "db_unavailable"
ERROR_SQL = "sql_error"
ERROR_BUSINESS = "business_error"
ERROR_EMPTY = "empty_data"
ERROR_UNKNOWN = "unknown_error"

def service_response(ok, data=None, message="", error_type=None, fallback_used=False):
    return {"ok": ok, "data": data, "message": message, "error_type": error_type, "fallback_used": fallback_used}

def success(data=None, message=""):
    return service_response(ok=True, data=data, message=message, error_type=None, fallback_used=False)

def fallback(data=None, message="", error_type=ERROR_UNKNOWN):
    return service_response(ok=False, data=data, message=message, error_type=error_type, fallback_used=True)

def business_error(message, data=None):
    return service_response(ok=False, data=data, message=message, error_type=ERROR_BUSINESS, fallback_used=False)

def empty_data(message="Данные не найдены.", data=None):
    return service_response(ok=False, data=data, message=message, error_type=ERROR_EMPTY, fallback_used=False)

businesserror = business_error
emptydata = empty_data

def detect_error_type(exception):
    if isinstance(exception, sqlite3.OperationalError):
        text = str(exception).lower()
        db_markers = ("unable to open database file", "database is locked", "database disk image is malformed", "readonly database", "no such table", "cannot open")
        if any(marker in text for marker in db_markers):
            return ERROR_DB_UNAVAILABLE
        return ERROR_SQL
    if isinstance(exception, sqlite3.DatabaseError):
        return ERROR_SQL
    if isinstance(exception, ValueError):
        return ERROR_BUSINESS
    return ERROR_UNKNOWN

def build_error_message(error_type, default_message=None):
    messages = {
        ERROR_DB_UNAVAILABLE: "Сервис базы данных временно недоступен.",
        ERROR_SQL: "Ошибка SQL-запроса.",
        ERROR_BUSINESS: "Ошибка бизнес-логики.",
        ERROR_EMPTY: "Данные не найдены.",
        ERROR_UNKNOWN: "Произошла неизвестная ошибка.",
    }
    if default_message:
        return default_message
    return messages.get(error_type, messages[ERROR_UNKNOWN])

def exception_fallback(exception, fallback_data=None, default_message=None):
    error_type = detect_error_type(exception)
    message = build_error_message(error_type, default_message)
    return fallback(data=fallback_data, message=message, error_type=error_type )

exceptionfallback = exception_fallback
