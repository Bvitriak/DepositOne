from fastapi.responses import JSONResponse

from services import contract_service


def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_payload(body):
    data = body or {}
    return {
        "deposit_id": data.get("deposit_id"),
        "contract_date": str(data.get("contract_date") or "").strip(),
        "signing_status": str(data.get("signing_status") or "").strip(),
        "description": str(data.get("description") or "").strip(),
        "special_conditions": str(data.get("special_conditions") or "").strip(),
    }


def is_incomplete(payload):
    if payload["deposit_id"] in (None, ""):
        return True
    for field in ["contract_date", "signing_status", "description", "special_conditions"]:
        if payload[field] == "":
            return True
    return False


def list_contracts(connection, query_params):
    search = (query_params.get("search") or "").strip()
    sort = query_params.get("sort") or "created"
    order = query_params.get("order") or "desc"
    page = to_int(query_params.get("page"), 1)
    page_size = to_int(query_params.get("page_size"), 10)
    result, status = contract_service.list_contracts(connection, search, sort, order, page, page_size)
    return JSONResponse(result, status_code=status)


def get_contract(connection, contract_id):
    result, status = contract_service.get_contract(connection, contract_id)
    return JSONResponse(result, status_code=status)


def create_contract(connection, body, user):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = contract_service.create_contract(connection, payload, user["id"])
    return JSONResponse(result, status_code=status)


def update_contract(connection, contract_id, body):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = contract_service.update_contract(connection, contract_id, payload)
    return JSONResponse(result, status_code=status)


def delete_contract(connection, contract_id):
    result, status = contract_service.delete_contract(connection, contract_id)
    return JSONResponse(result, status_code=status)
