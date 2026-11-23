from fastapi.responses import JSONResponse

from services import contract_service
from utils.params import read_list_params


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
    for field in ["contract_date", "signing_status", "description"]:
        if payload[field] == "":
            return True
    return False


def list_contracts(connection, query_params):
    search, sort, order, page, page_size = read_list_params(query_params, "created", "desc")
    status_filter = query_params.get("status") or ""
    if status_filter not in contract_service.SIGNING_STATUSES:
        status_filter = ""
    result, response_status = contract_service.list_contracts(connection, search, status_filter, sort, order, page, page_size)
    return JSONResponse(result, status_code=response_status)


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
