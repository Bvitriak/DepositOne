from fastapi.responses import JSONResponse

from services import depositor_service
from utils.params import read_list_params

REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth", "passport", "tin", "phone", "email", "address"]


def build_payload(body):
    data = body or {}
    return {
        "first_name": str(data.get("first_name") or "").strip(),
        "last_name": str(data.get("last_name") or "").strip(),
        "date_of_birth": str(data.get("date_of_birth") or "").strip(),
        "country_id": data.get("country_id"),
        "passport": str(data.get("passport") or "").strip(),
        "tin": str(data.get("tin") or "").strip(),
        "phone": str(data.get("phone") or "").strip(),
        "email": str(data.get("email") or "").strip(),
        "address": str(data.get("address") or "").strip(),
    }


def is_incomplete(payload):
    for field in REQUIRED_FIELDS:
        if payload[field] == "":
            return True
    return payload["country_id"] in (None, "")


def list_depositors(connection, query_params):
    search, sort, order, page, page_size = read_list_params(query_params, "created", "desc")
    result, status = depositor_service.list_depositors(connection, search, sort, order, page, page_size)
    return JSONResponse(result, status_code=status)


def list_options(connection):
    result, status = depositor_service.list_options(connection)
    return JSONResponse(result, status_code=status)


def get_depositor(connection, depositor_id):
    result, status = depositor_service.get_depositor(connection, depositor_id)
    return JSONResponse(result, status_code=status)


def create_depositor(connection, body, user):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = depositor_service.create_depositor(connection, payload, user["id"])
    return JSONResponse(result, status_code=status)


def update_depositor(connection, depositor_id, body):
    payload = build_payload(body)
    if is_incomplete(payload):
        return JSONResponse({"error": "all fields are required"}, status_code=400)
    result, status = depositor_service.update_depositor(connection, depositor_id, payload)
    return JSONResponse(result, status_code=status)


def delete_depositor(connection, depositor_id):
    result, status = depositor_service.delete_depositor(connection, depositor_id)
    return JSONResponse(result, status_code=status)
