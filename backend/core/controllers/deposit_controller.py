from fastapi.responses import JSONResponse

from services import deposit_service


def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_payload(body):
    data = body or {}
    return {
        "depositor_id": data.get("depositor_id"),
        "currency_id": data.get("currency_id"),
        "status": str(data.get("status") or "").strip(),
        "amount": str(data.get("amount") or "").strip(),
        "interest_rate": str(data.get("interest_rate") or "").strip(),
        "start_date": str(data.get("start_date") or "").strip(),
        "end_date": str(data.get("end_date") or "").strip(),
    }


def is_incomplete(payload):
    if payload["depositor_id"] in (None, ""):
        return True
    if payload["currency_id"] in (None, ""):
        return True
    for field in ["status", "amount", "interest_rate", "start_date", "end_date"]:
        if payload[field] == "":
            return True
    return False


def list_deposits(connection, query_params):
    search = (query_params.get("search") or "").strip()
    sort = query_params.get("sort") or "created"
    order = query_params.get("order") or "desc"
    page = to_int(query_params.get("page"), 1)
    page_size = to_int(query_params.get("page_size"), 10)
    result, status = deposit_service.list_deposits(connection, search, sort, order, page, page_size)
    return JSONResponse(result, status_code=status)


def list_options(connection):
    result, status = deposit_service.list_options(connection)
    return JSONResponse(result, status_code=status)


def get_stats(connection):
    result, status = deposit_service.get_stats(connection)
    return JSONResponse(result, status_code=status)


def get_deposit(connection, deposit_id):
    result, status = deposit_service.get_deposit(connection, deposit_id)
    return JSONResponse(result, status_code=status)


def create_deposit(connection, body, user):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = deposit_service.create_deposit(connection, payload, user["id"])
    return JSONResponse(result, status_code=status)


def update_deposit(connection, deposit_id, body):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = deposit_service.update_deposit(connection, deposit_id, payload)
    return JSONResponse(result, status_code=status)


def delete_deposit(connection, deposit_id):
    result, status = deposit_service.delete_deposit(connection, deposit_id)
    return JSONResponse(result, status_code=status)
