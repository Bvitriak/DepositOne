from __future__ import annotations
import sqlite3
from datetime import date
from core_service.app.db import refresh_slave_after_write
from core_service.app.models.contract import ContractModel
from core_service.app.utils.fallbacks import (business_error, empty_data, exception_fallback, success )

def generate_contract_number(db=None) -> str:
    model = ContractModel(db=db)
    today = date.today()
    today_iso = today.isoformat()
    today_str = today.strftime("%Y%m%d")
    row = model.count_by_contract_date(today_iso)
    count_today = row["cnt"] + 1
    return f"DEP-{today_str}-{count_today:04d}"

def create_contract(deposit_id: int, created_by_user_id: int, term_description: str | None = None, special_conditions: str | None = None, db=None ):
    try:
        model = ContractModel(db=db)

        if not model.deposit_exists(deposit_id):
            return business_error("Вклад не найден.")

        existing = model.find_by_deposit_id(deposit_id)
        if existing is not None:
            return business_error(
                f"Договор уже существует: {existing['contract_number']}.",
                data={
                    "id": existing["id"],
                    "contract_number": existing["contract_number"],
                    "deposit_id": deposit_id,
                },
            )

        contract_number = generate_contract_number(db=db)
        contract_date = date.today().isoformat()

        model.create_contract(
            deposit_id=deposit_id,
            created_by_user_id=created_by_user_id,
            contract_number=contract_number,
            contract_date=contract_date,
            term_description=term_description,
            special_conditions=special_conditions,
            is_signed=1,
        )
        refresh_slave_after_write()

        row = model.get_by_contract_number(contract_number)
        return success(row, "Договор успешно создан.")

    except sqlite3.Error as exc:
        fallback_data = {
            "id": None,
            "contract_number": "UNAVAILABLE",
            "contract_date": date.today().isoformat(),
            "deposit_id": deposit_id,
            "term_description": term_description,
            "special_conditions": special_conditions,
            "is_signed": 0,
        }
        return exception_fallback(
            exc,
            fallback_data=fallback_data,
            default_message="Ошибка при создании договора.",
        )

def get_contract_data(contract_id: int, db=None):
    try:
        model = ContractModel(db=db)
        row = model.get_contract_data(contract_id)

        if row is None:
            return empty_data("Договор не найден.", data=None)

        data = {
            "contract_number": row["contract_number"],
            "contract_date": row["contract_date"],
            "depositor_full_name": (
                f"{row['last_name']} {row['first_name']} {row['middle_name'] or ''}"
            ).strip(),
            "passport_series": row["passport_series"],
            "passport_number": row["passport_number"],
            "address": row["address"],
            "phone": row["phone"],
            "deposit_type": row["deposit_type"],
            "amount": row["amount"],
            "interest_rate": row["interest_rate"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "capitalization": row["capitalization"],
            "auto_renewal": row["auto_renewal"],
            "special_conditions": row["special_conditions"],
        }
        return success(data)

    except sqlite3.Error as exc:
        fallback_data = {
            "contract_number": "UNAVAILABLE",
            "contract_date": date.today().isoformat(),
            "depositor_full_name": "",
            "passport_series": "-",
            "passport_number": "-",
            "address": "-",
            "phone": "-",
            "deposit_type": "",
            "amount": "0.00",
            "interest_rate": "0.00",
            "start_date": "-",
            "end_date": "-",
            "capitalization": 0,
            "auto_renewal": 0,
            "special_conditions": "",
        }
        return exception_fallback(
            exc,
            fallback_data=fallback_data,
            default_message="Ошибка при получении договора.",
        )
