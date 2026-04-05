from __future__ import annotations
import sqlite3
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from core_service.app.constants import DAYS_IN_YEAR, DepositStatus, TWOPLACES
from core_service.app.db import get_db, refresh_slave_after_write
from core_service.app.utils.fallbacks import (business_error, empty_data, exception_fallback, success )
from core_service.app.utils.types import ServiceResult

MoneyLike = Decimal | int | float | str

def calculate_days(start_date: str, end_date: str) -> int:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    return (end - start).days

def calculate_interest(amount: MoneyLike, annual_rate: MoneyLike, days: int) -> Decimal:
    amount_dec = Decimal(str(amount))
    annual_rate_dec = Decimal(str(annual_rate))
    days_dec = Decimal(days)
    interest = amount_dec * annual_rate_dec / Decimal("100") * days_dec / DAYS_IN_YEAR
    return interest.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def calculate_total_amount(amount: MoneyLike, interest_amount: MoneyLike) -> Decimal:
    total = Decimal(str(amount)) + Decimal(str(interest_amount))
    return total.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def calculate_deposit_return(deposit_row: sqlite3.Row) -> dict[str, str | int]:
    days = calculate_days(deposit_row["start_date"], deposit_row["end_date"])
    interest_amount = calculate_interest(
        deposit_row["amount"],
        deposit_row["interest_rate"],
        days,
    )
    total_amount = calculate_total_amount(deposit_row["amount"], interest_amount)
    return {
        "deposit_id": deposit_row["id"],
        "days": days,
        "interest_amount": str(interest_amount),
        "total_amount": str(total_amount),
    }

def create_accrual_for_deposit(deposit_id: int) -> ServiceResult:
    try:
        db = get_db()

        deposit = db.execute(
            """
            SELECT
                id,
                amount,
                interest_rate,
                start_date,
                end_date,
                status,
                capitalization,
                auto_renewal
            FROM deposits
            WHERE id = ?
            """,
            (deposit_id,),
        ).fetchone()

        if deposit is None:
            return business_error("Вклад не найден.")

        if str(deposit["status"]).lower() != DepositStatus.ACTIVE.value:
            return business_error("Начисление возможно только для активного вклада.")

        result = calculate_deposit_return(deposit)
        interest_amount = Decimal(str(result["interest_amount"]))
        accrual_date = date.today().isoformat()

        db.execute(
            """
            INSERT INTO interest_accruals (deposit_id, accrual_date, amount)
            VALUES (?, ?, ?)
            """,
            (deposit_id, accrual_date, float(interest_amount)),
        )

        if int(deposit["capitalization"]) == 1:
            new_amount = Decimal(str(deposit["amount"])) + interest_amount
            new_amount = new_amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

            db.execute(
                """
                UPDATE deposits
                SET amount = ?
                WHERE id = ?
                """,
                (float(new_amount), deposit_id),
            )

        db.execute(
            """
            INSERT INTO transactions (deposit_id, operation_type, amount, operation_date)
            VALUES (?, ?, ?, ?)
            """,
            (deposit_id, "interest_payment", float(interest_amount), datetime.now().isoformat(sep=" ")),
        )

        db.commit()
        refresh_slave_after_write()

        return success(
            {
                **result,
                "accrual_date": accrual_date,
                "capitalized": bool(deposit["capitalization"]),
            },
            "Проценты успешно начислены.",
        )

    except (sqlite3.Error, ValueError, InvalidOperation) as exc:
        return exception_fallback(
            exc,
            fallback_data=None,
            default_message="Ошибка при создании начисления.",
        )

def get_deposits_for_return_tomorrow():
    try:
        db = get_db()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        deposits = db.execute(
            "SELECT id, amount, interest_rate, start_date, end_date FROM deposits WHERE end_date = ? AND status = ? ORDER BY id DESC",
            (tomorrow, DepositStatus.ACTIVE.value),
        ).fetchall()
        if not deposits:
            return empty_data("На завтра возвратов нет.", data=[])
        return success([calculate_deposit_return(row) for row in deposits])
    except (sqlite3.Error, ValueError, InvalidOperation) as exc:
        return exception_fallback(
            exc,
            fallback_data=[],
            default_message="Не удалось получить возвраты на завтра.",
        )

def get_month_return_plan(year: int, month: int) -> ServiceResult:
    try:
        db = get_db()

        start_dt = date(year, month, 1)
        if month == 12:
            end_dt = date(year + 1, 1, 1)
        else:
            end_dt = date(year, month + 1, 1)

        deposits = db.execute(
            """
            SELECT id, amount, interest_rate, start_date, end_date
            FROM deposits
            WHERE end_date >= ? AND end_date < ? AND status = ?
            ORDER BY end_date ASC, id ASC
            """,
            (
                start_dt.isoformat(),
                end_dt.isoformat(),
                DepositStatus.ACTIVE.value,
            ),
        ).fetchall()

        items = [calculate_deposit_return(row) for row in deposits]
        total_sum = sum(Decimal(item["total_amount"]) for item in items) if items else Decimal("0.00")

        data = {
            "items": items,
            "total_sum": str(total_sum.quantize(TWOPLACES, rounding=ROUND_HALF_UP)),
        }

        if not items:
            return empty_data("В этом месяце возвратов нет.", data=data)

        return success(data, "План возвратов на месяц сформирован.")
    except (sqlite3.Error, ValueError, InvalidOperation) as exc:
        return exception_fallback(
            exc,
            fallback_data={"items": [], "total_sum": "0.00"},
            default_message="Не удалось сформировать месячный план возвратов.",
        )
