from __future__ import annotations
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from core_service.app.constants import DepositStatus, OperationType, TWOPLACES
from core_service.app.db import get_db, refresh_slave_after_write
from core_service.app.models.deposit import DepositModel
from core_service.app.models.dto import DepositData
from core_service.app.utils.fallbacks import business_error, exception_fallback, success
from core_service.app.utils.types import ServiceResult

def create_deposit(payload: DepositData, db=None) -> ServiceResult:
    try:
        model = DepositModel(db=db)
        cursor = model.create_deposit(
            depositor_id=payload.depositor_id,
            opened_by_user_id=payload.opened_by_user_id,
            deposit_type=payload.deposit_type,
            amount=payload.amount,
            interest_rate=payload.interest_rate,
            start_date=payload.start_date,
            end_date=payload.end_date,
            currency=payload.currency,
            capitalization=payload.capitalization,
            auto_renewal=payload.auto_renewal,
            status=payload.status,
        )
        return success({"id": cursor.lastrowid}, "Вклад успешно создан.")
    except sqlite3.IntegrityError:
        return business_error(
            "Не удалось создать вклад из-за нарушения ограничений данных.",
            data=None,
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data=None,
            default_message="Не удалось создать вклад.",
        )

def update_deposit(deposit_id: int, payload: DepositData, db=None ) -> ServiceResult:
    try:
        model = DepositModel(db=db)
        existing = model.get_by_id(deposit_id)
        if not existing:
            return business_error("Вклад не найден.", data=None)

        model.update_deposit(
            deposit_id=deposit_id,
            depositor_id=payload.depositor_id,
            deposit_type=payload.deposit_type,
            amount=payload.amount,
            interest_rate=payload.interest_rate,
            start_date=payload.start_date,
            end_date=payload.end_date,
            currency=payload.currency,
            capitalization=payload.capitalization,
            auto_renewal=payload.auto_renewal,
            status=payload.status,
        )
        return success({"id": deposit_id}, "Вклад успешно обновлён.")
    except sqlite3.IntegrityError:
        return business_error(
            "Не удалось обновить вклад из-за нарушения ограничений данных.",
            data={"id": deposit_id},
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data={"id": deposit_id},
            default_message="Не удалось обновить вклад.",
        )

def delete_deposit(deposit_id: int, db=None) -> ServiceResult:
    try:
        model = DepositModel(db=db)
        existing = model.get_by_id(deposit_id)
        if not existing:
            return business_error("Вклад не найден.", data=None)

        model.delete_deposit(deposit_id)
        return success({"id": deposit_id}, "Вклад удалён.")
    except sqlite3.IntegrityError:
        return business_error(
            "Нельзя удалить вклад, связанный с договором, начислениями или операциями.",
            data={"id": deposit_id},
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data={"id": deposit_id},
            default_message="Не удалось удалить вклад.",
        )

def get_deposit_for_edit(deposit_id: int, db=None) -> ServiceResult:
    try:
        model = DepositModel(db=db)
        row = model.get_by_id(deposit_id)
        if not row:
            return business_error("Вклад не найден.", data=None)
        return success(dict(row), "Данные вклада загружены.")
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data=None,
            default_message="Не удалось загрузить данные вклада.",
        )

def topup_deposit(deposit_id: int, amount: float, db=None) -> ServiceResult:
    try:
        db = db or get_db()
        model = DepositModel(db=db)

        deposit = model.get_by_id(deposit_id)
        if not deposit:
            return business_error("Вклад не найден.", data=None)

        if str(deposit["status"]).lower() != DepositStatus.ACTIVE.value:
            return business_error(
                "Пополнение возможно только для активного вклада.",
                data={"id": deposit_id},
            )

        try:
            topup_amount = Decimal(str(amount)).quantize(
                TWOPLACES,
                rounding=ROUND_HALF_UP,
            )
        except (InvalidOperation, ValueError):
            return business_error(
                "Некорректная сумма пополнения.",
                data={"id": deposit_id},
            )

        if topup_amount <= Decimal("0.00"):
            return business_error(
                "Сумма пополнения должна быть больше нуля.",
                data={"id": deposit_id},
            )

        old_amount = Decimal(str(deposit["amount"])).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )
        new_amount = (old_amount + topup_amount).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )
        operation_date = datetime.now().isoformat(sep=" ")

        db.execute(
            "UPDATE deposits SET amount = ? WHERE id = ?",
            (float(new_amount), deposit_id),
        )

        db.execute(
            """
            INSERT INTO transactions 
                (deposit_id, operation_type, amount, operation_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                deposit_id,
                OperationType.DEPOSIT_TOPUP.value,
                float(topup_amount),
                operation_date,
            ),
        )

        db.commit()
        refresh_slave_after_write()

        return success(
            {
                "id": deposit_id,
                "topup_amount": str(topup_amount),
                "old_amount": str(old_amount),
                "new_amount": str(new_amount),
            },
            "Вклад успешно пополнен.",
        )

    except sqlite3.Error as exc:
        print("TOPUP ERROR:", repr(exc))
        return exception_fallback(
            exc,
            fallback_data={"id": deposit_id},
            default_message="Не удалось пополнить вклад.",
        )
