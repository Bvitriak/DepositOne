from datetime import date

from repositories import contract_repository, deposit_repository
from services import deposit_service

PAGE_SIZES = [10, 25, 50]
SIGNING_STATUSES = ["Signed", "Pending", "Rejected"]


def serialize(contract):
    amount = float(contract.amount)
    interest_rate = float(contract.interest_rate)
    days = deposit_service.term_days(contract.start_date, contract.end_date)
    term_end_accruals = deposit_service.interest(amount, interest_rate, days)
    deposit_number = "D-" + str(contract.deposit_ordinal).zfill(4)
    year = str(contract.contract_date.year)
    month = str(contract.contract_date.month).zfill(2)
    return {
        "id": contract.id,
        "contract_code": "K-" + str(contract.ordinal).zfill(4),
        "contract_number": year + "/" + month + "/" + deposit_number,
        "deposit_id": contract.deposit_id,
        "deposit_number": deposit_number,
        "depositor_id": contract.depositor_id,
        "depositor": contract.depositor_name,
        "currency": contract.currency,
        "amount": amount,
        "interest_rate": interest_rate,
        "term_end_accruals": term_end_accruals,
        "start_date": contract.start_date.isoformat(),
        "end_date": contract.end_date.isoformat(),
        "contract_date": contract.contract_date.isoformat(),
        "signing_status": contract.signing_status,
        "description": contract.description,
        "special_conditions": contract.special_conditions,
    }


def validate(connection, payload, contract_id):
    try:
        payload["deposit_id"] = int(payload["deposit_id"])
    except (TypeError, ValueError):
        return "deposit is invalid"
    if not deposit_repository.get_deposit(connection, payload["deposit_id"]):
        return "deposit is invalid"
    if contract_repository.count_by_deposit(connection, payload["deposit_id"], contract_id) > 0:
        return "deposit already has a contract"
    if payload["signing_status"] not in SIGNING_STATUSES:
        return "signing status is invalid"
    try:
        payload["contract_date"] = date.fromisoformat(payload["contract_date"])
    except ValueError:
        return "contract date is invalid"
    return None


def list_contracts(connection, search, status, sort, order, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    total = contract_repository.count_contracts(connection, search, status)
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    contracts = contract_repository.list_contracts(connection, search, status, sort, order, page_size, offset)
    items = [serialize(contract) for contract in contracts]
    return {"contracts": items, "total": total, "page": page, "pages": pages, "page_size": page_size}, 200


def get_contract(connection, contract_id):
    contract = contract_repository.get_contract(connection, contract_id)
    if not contract:
        return {"error": "contract not found"}, 404
    return serialize(contract), 200


def create_contract(connection, payload, user_id):
    error = validate(connection, payload, 0)
    if error:
        return {"error": error}, 400
    contract = contract_repository.create_contract(connection, payload, user_id)
    return serialize(contract), 201


def update_contract(connection, contract_id, payload):
    error = validate(connection, payload, contract_id)
    if error:
        return {"error": error}, 400
    contract = contract_repository.update_contract(connection, contract_id, payload)
    if not contract:
        return {"error": "contract not found"}, 404
    return serialize(contract), 200


def delete_contract(connection, contract_id):
    contract = contract_repository.get_contract(connection, contract_id)
    if not contract:
        return {"error": "contract not found"}, 404
    contract_repository.delete_contract(connection, contract_id)
    return {"deleted": True}, 200
