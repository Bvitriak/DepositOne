from datetime import datetime
from typing import Any
from flask import abort, flash
from core_service.app.constants import (CURRENCIES, DEPOSIT_STATUSES, CurrencyCode, DepositStatus, REMEMBER_CHECKBOX_VALUE )
from core_service.app.db import get_db
from core_service.app.models.depositor import DepositorModel
from core_service.app.models.dto import DepositorData, DepositData
from core_service.app.utils.fallbacks import ( ERROR_BUSINESS, ERROR_DB_UNAVAILABLE, ERROR_EMPTY, ERROR_SQL )
from core_service.app.utils.types import ServiceResult

def get_row_or_404(query: str, params: tuple[Any, ...] = ()) -> Any:
    row = get_db().execute(query, params).fetchone()
    if row is None:
        abort(404)
    return row

def flash_service_message(result: ServiceResult | None) -> None:
    if not result or not result.get("message"):
        return

    error_type = result.get("error_type")
    if error_type == ERROR_EMPTY:
        flash(result["message"], "warning")
    elif error_type == ERROR_BUSINESS:
        flash(result["message"], "error")
    elif error_type in (ERROR_DB_UNAVAILABLE, ERROR_SQL):
        flash(result["message"], "error")
    elif result.get("ok"):
        flash(result["message"], "success")
    else:
        flash(result["message"], "error")

def safe_int(value: Any, default: int | None = None, minimum: int | None = None ) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    if minimum is not None and parsed < minimum:
        return default
    return parsed

def safe_float( value: Any, default: float | None = None, minimum: float | None = None ) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed

def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None

def load_depositors_for_select() -> list[dict[str, Any]]:
    model = DepositorModel()
    rows = model.list_for_select()
    result: list[dict[str, Any]] = []
    for row in rows:
        result.append(
            {
                "id": row["id"],
                "lastname": row["lastname"],
                "firstname": row["firstname"],
                "middlename": row["middlename"],
            }
        )
    return result

def empty_paginated_depositors() -> dict[str, Any]:
    return {
        "items": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 0,
            "total_pages": 0,
            "has_prev": False,
            "has_next": False,
        },
        "filters": {"search": "", "phone": "", "email": ""},
        "sorting": {"sort_by": "id", "sort_order": "desc"},
    }

def empty_paginated_deposits() -> dict[str, Any]:
    return {
        "items": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 0,
            "total_pages": 0,
            "has_prev": False,
            "has_next": False,
        },
        "filters": {
            "search": "",
            "status": "",
            "currency": "",
            "min_amount": "",
            "max_amount": "",
        },
        "sorting": {"sort_by": "id", "sort_order": "desc"},
    }

def empty_paginated_contracts() -> dict[str, Any]:
    return {
        "items": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 0,
            "total_pages": 0,
            "has_prev": False,
            "has_next": False,
        },
        "filters": {"search": "", "is_signed": ""},
        "sorting": {"sort_by": "id", "sort_order": "desc"},
    }

def validate_depositor_form(form, *, created_by_user_id: int ) -> tuple[DepositorData | None, str | None]:
    last_name = normalize_text(form.get("lastname"))
    first_name = normalize_text(form.get("firstname"))
    middle_name = normalize_text(form.get("middlename"))
    passport_series = normalize_text(form.get("passportseries"))
    passport_number = normalize_text(form.get("passportnumber"))
    issued_by = normalize_text(form.get("issuedby"))
    phone = normalize_text(form.get("phone"))
    email = normalize_text(form.get("email"))
    address = normalize_text(form.get("address"))

    if not last_name or not first_name or not passport_series or not passport_number:
        return None, "Фамилия, имя, серия и номер паспорта обязательны."

    return DepositorData(
        created_by_user_id=created_by_user_id,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        passport_series=passport_series,
        passport_number=passport_number,
        issued_by=issued_by,
        phone=phone,
        email=email,
        address=address,
    ), None

def validate_deposit_form(form, opened_by_user_id: int):
    depositor_id = safe_int(form.get("depositor_id"), minimum=1)
    deposit_type = normalize_text(form.get("deposit_type"))
    amount = safe_float(form.get("amount"), minimum=0)
    interest_rate = safe_float(form.get("interest_rate"), minimum=0)
    start_date = normalize_text(form.get("start_date"))
    end_date = normalize_text(form.get("end_date"))
    currency = normalize_text(form.get("currency")) or CurrencyCode.RUB.value
    capitalization = 1 if form.get("capitalization") == REMEMBER_CHECKBOX_VALUE else 0
    auto_renewal = 1 if form.get("auto_renewal") == REMEMBER_CHECKBOX_VALUE else 0
    status = normalize_text(form.get("status")) or DepositStatus.ACTIVE.value

    if not depositor_id or not deposit_type or amount is None or interest_rate is None:
        return None, "Заполните обязательные поля."

    if not start_date or not end_date:
        return None, "Укажите даты вклада."

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return None, "Дата должна быть в формате YYYY-MM-DD."

    if end_dt < start_dt:
        return None, "Дата окончания не может быть раньше даты начала."

    if status not in DEPOSIT_STATUSES:
        return None, f"Недопустимый статус. Возможные значения: {', '.join(DEPOSIT_STATUSES)}."

    if currency not in CURRENCIES:
        return None, f"Недопустимая валюта. Возможные значения: {', '.join(CURRENCIES)}."

    return DepositData(
        depositor_id=depositor_id,
        opened_by_user_id=opened_by_user_id,
        deposit_type=deposit_type,
        amount=amount,
        interest_rate=interest_rate,
        start_date=start_date,
        end_date=end_date,
        currency=currency,
        capitalization=capitalization,
        auto_renewal=auto_renewal,
        status=status,
    ), None
