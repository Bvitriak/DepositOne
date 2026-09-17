from datetime import date

from repositories import depositor_repository, country_repository, deposit_repository

PAGE_SIZES = [10, 25, 50]


def count_active_deposits(connection, depositor_id):
    return deposit_repository.count_active_by_depositor(connection, depositor_id)


def list_options(connection):
    return {"depositors": depositor_repository.list_options(connection)}, 200


def serialize(depositor, active_deposits):
    return {
        "id": depositor.id,
        "first_name": depositor.first_name,
        "last_name": depositor.last_name,
        "date_of_birth": depositor.date_of_birth.isoformat(),
        "country_id": depositor.country_id,
        "country": depositor.country,
        "passport": depositor.passport,
        "tin": depositor.tin,
        "phone": depositor.phone,
        "email": depositor.email,
        "address": depositor.address,
        "active_deposits": active_deposits,
        "opened": depositor.created_at.date().isoformat(),
    }


def validate(connection, payload):
    try:
        payload["date_of_birth"] = date.fromisoformat(payload["date_of_birth"])
    except ValueError:
        return "date of birth is invalid"
    try:
        payload["country_id"] = int(payload["country_id"])
    except (TypeError, ValueError):
        return "country is invalid"
    if not country_repository.country_exists(connection, payload["country_id"]):
        return "country is invalid"
    return None


def list_depositors(connection, search, sort, order, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    total = depositor_repository.count_depositors(connection, search)
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    depositors = depositor_repository.list_depositors(connection, search, sort, order, page_size, offset)
    items = [serialize(depositor, count_active_deposits(connection, depositor.id)) for depositor in depositors]
    return {"depositors": items, "total": total, "page": page, "pages": pages, "page_size": page_size}, 200


def get_depositor(connection, depositor_id):
    depositor = depositor_repository.get_depositor(connection, depositor_id)
    if not depositor:
        return {"error": "depositor not found"}, 404
    return serialize(depositor, count_active_deposits(connection, depositor_id)), 200


def create_depositor(connection, payload, user_id):
    error = validate(connection, payload)
    if error:
        return {"error": error}, 400
    depositor = depositor_repository.create_depositor(connection, payload, user_id)
    return serialize(depositor, count_active_deposits(connection, depositor.id)), 201


def update_depositor(connection, depositor_id, payload):
    error = validate(connection, payload)
    if error:
        return {"error": error}, 400
    depositor = depositor_repository.update_depositor(connection, depositor_id, payload)
    if not depositor:
        return {"error": "depositor not found"}, 404
    return serialize(depositor, count_active_deposits(connection, depositor_id)), 200


def delete_depositor(connection, depositor_id):
    depositor = depositor_repository.get_depositor(connection, depositor_id)
    if not depositor:
        return {"error": "depositor not found"}, 404
    if count_active_deposits(connection, depositor_id) > 0:
        return {"error": "depositor has active deposits", "deletable": False}, 409
    depositor_repository.delete_depositor(connection, depositor_id)
    return {"deleted": True}, 200
