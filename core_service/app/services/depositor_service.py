from __future__ import annotations
import sqlite3
from typing import Any
from core_service.app.models.depositor import DepositorModel
from core_service.app.models.dto import DepositorData
from core_service.app.utils.fallbacks import businesserror, exceptionfallback, success
from core_service.app.utils.types import ServiceResult

def map_integrity_error(
    exc: sqlite3.IntegrityError,
    depositor_id: int | None = None,
) -> ServiceResult:
    message = str(exc).lower()
    data: dict[str, Any] | None = {"id": depositor_id} if depositor_id is not None else None

    if "unique" in message and (
        "passportseries" in message
        or "passportnumber" in message
        or "depositors.passportseries" in message
        or "depositors.passportnumber" in message
    ):
        return businesserror(
            "Вкладчик с такими паспортными данными уже существует.",
            data=data,
        )

    if "foreign key constraint failed" in message:
        return businesserror(
            "Не найден пользователь, от имени которого создаётся вкладчик.",
            data=data,
        )

    if "not null constraint failed" in message:
        return businesserror(
            f"Не заполнено обязательное поле в базе данных: {exc}",
            data=data,
        )

    return businesserror(
        f"Ошибка целостности данных: {exc}",
        data=data,
    )

def create_depositor(payload: DepositorData, created_by_user_id: int, db=None ) -> ServiceResult:
    try:
        model = DepositorModel(db=db)
        cursor = model.create_depositor(
            created_by_user_id,
            payload.last_name,
            payload.first_name,
            payload.middle_name,
            payload.passport_series,
            payload.passport_number,
            payload.issued_by,
            payload.phone,
            payload.email,
            payload.address,
        )
        return success({"id": cursor.lastrowid}, "Вкладчик успешно создан.")
    except sqlite3.IntegrityError as exc:
        return map_integrity_error(exc)
    except sqlite3.Error as exc:
        return exceptionfallback(
            exc,
            fallbackdata=None,
            defaultmessage="Не удалось создать вкладчика.",
        )

def update_depositor(depositorid: int, payload: dict[str, Any], db=None ) -> ServiceResult:
    try:
        model = DepositorModel(db=db)
        existing = model.get_by_id(depositorid)
        if not existing:
            return businesserror("Вкладчик не найден.", data=None)

        model.update_depositor(
            depositorid,
            payload["lastname"],
            payload["firstname"],
            payload.get("middlename"),
            payload["passportseries"],
            payload["passportnumber"],
            payload.get("issuedby"),
            payload.get("phone"),
            payload.get("email"),
            payload.get("address"),
        )
        return success({"id": depositorid}, "Данные вкладчика обновлены.")
    except sqlite3.IntegrityError as exc:
        return map_integrity_error(exc, depositorid=depositorid)
    except sqlite3.Error as exc:
        return exceptionfallback(
            exc,
            fallbackdata={"id": depositorid},
            defaultmessage="Не удалось обновить вкладчика.",
        )

def delete_depositor(depositor_id: int, db=None ) -> ServiceResult:
    try:
        model = DepositorModel(db=db)
        existing = model.get_by_id(depositor_id)
        if not existing:
            return businesserror("Вкладчик не найден.", data=None)

        model.delete_depositor(depositor_id)
        return success({"id": depositor_id}, "Вкладчик удалён.")
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "foreign key constraint failed" in message:
            return businesserror(
                "Нельзя удалить вкладчика, так как он связан с другими данными.",
                data={"id": depositor_id},
            )
        return businesserror(
            f"Ошибка целостности данных: {exc}",
            data={"id": depositor_id},
        )
    except sqlite3.Error as exc:
        return exceptionfallback(
            exc,
            fallbackdata={"id": depositor_id},
            defaultmessage="Не удалось удалить вкладчика.",
        )

def get_depositor_for_edit(depositorid: int, db=None ) -> ServiceResult:
    try:
        model = DepositorModel(db=db)
        row = model.get_by_id(depositorid)
        if not row:
            return businesserror("Вкладчик не найден.", data=None)

        return success(dict(row), "Данные вкладчика загружены.")
    except sqlite3.Error as exc:
        return exceptionfallback(
            exc,
            fallbackdata=None,
            defaultmessage="Не удалось загрузить данные вкладчика.",
        )
