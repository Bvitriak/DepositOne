from __future__ import annotations
import sqlite3
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from core_service.app.constants import (EXPENSE_OPERATION_TYPES, INCOME_OPERATION_TYPES, TWOPLACES )
from core_service.app.db import get_db
from core_service.app.utils.fallbacks import empty_data, exception_fallback, success
from core_service.app.utils.types import ServiceResult

def normalize_money(value: Any) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def _cash_flow_result(start_dt: datetime, end_dt: datetime, income: Decimal, expense: Decimal ) -> dict[str, str]:
    balance = (income - expense).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return {
        "start": start_dt.isoformat(sep=" "),
        "end": end_dt.isoformat(sep=" "),
        "income": str(income),
        "expense": str(expense),
        "balance": str(balance),
    }

def get_cash_flow_by_period(start_dt: datetime, end_dt: datetime) -> ServiceResult:
    try:
        db = get_db()
        totals_row = db.execute(
            """
            SELECT
                COALESCE(SUM(CASE
                    WHEN operation_type IN (?, ?) THEN amount ELSE 0
                END), 0) AS income,
                COALESCE(SUM(CASE
                    WHEN operation_type IN (?, ?) THEN amount ELSE 0
                END), 0) AS expense
            FROM transactions
            WHERE operation_date BETWEEN ? AND ?
            """,
            (
                INCOME_OPERATION_TYPES[0],
                INCOME_OPERATION_TYPES[1],
                EXPENSE_OPERATION_TYPES[0],
                EXPENSE_OPERATION_TYPES[1],
                start_dt.isoformat(sep=" "),
                end_dt.isoformat(sep=" "),
            ),
        ).fetchone()

        income = normalize_money(totals_row["income"] if totals_row else 0)
        expense = normalize_money(totals_row["expense"] if totals_row else 0)

        return success(
            _cash_flow_result(start_dt, end_dt, income, expense),
            "Отчет сформирован.",
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data=_cash_flow_result(
                start_dt,
                end_dt,
                Decimal("0.00"),
                Decimal("0.00"),
            ),
            default_message="Не удалось сформировать отчет по движению средств.",
        )

def get_today_cash_flow() -> ServiceResult:
    start_dt = datetime.combine(date.today(), datetime.min.time())
    end_dt = datetime.combine(date.today(), datetime.max.time())
    return get_cash_flow_by_period(start_dt, end_dt)

def get_month_cash_flow(year: int, month: int) -> ServiceResult:
    start_dt = datetime(year, month, 1)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_year_cash_flow(year: int) -> ServiceResult:
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_five_year_cash_flow(start_year: int) -> ServiceResult:
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(start_year + 5, 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_all_depositors_summary() -> ServiceResult:
    try:
        db = get_db()
        rows = db.execute(
            """
            WITH deposit_stats AS (
                SELECT
                    d.depositor_id AS depositor_id,
                    COUNT(d.id) AS deposits_count,
                    COALESCE(SUM(d.amount), 0) AS total_deposit_amount
                FROM deposits d
                GROUP BY d.depositor_id
            ),
            interest_stats AS (
                SELECT
                    d.depositor_id AS depositor_id,
                    COALESCE(SUM(ia.amount), 0) AS total_interest
                FROM deposits d
                LEFT JOIN interest_accruals ia ON ia.deposit_id = d.id
                GROUP BY d.depositor_id
            ),
            transaction_stats AS (
                SELECT
                    d.depositor_id AS depositor_id,
                    COALESCE(SUM(CASE
                        WHEN t.operation_type IN (?, ?) THEN t.amount ELSE 0
                    END), 0) AS total_income,
                    COALESCE(SUM(CASE
                        WHEN t.operation_type IN (?, ?) THEN t.amount ELSE 0
                    END), 0) AS total_expense
                FROM deposits d
                LEFT JOIN transactions t ON t.deposit_id = d.id
                GROUP BY d.depositor_id
            )
            SELECT
                dep.id AS depositor_id,
                TRIM(dep.lastname || ' ' || dep.firstname || ' ' || COALESCE(dep.middlename, '')) AS full_name,
                COALESCE(ds.deposits_count, 0) AS deposits_count,
                COALESCE(ds.total_deposit_amount, 0) AS total_deposit_amount,
                COALESCE(is2.total_interest, 0) AS total_interest,
                COALESCE(ts.total_income, 0) AS total_income,
                COALESCE(ts.total_expense, 0) AS total_expense
            FROM depositors dep
            LEFT JOIN deposit_stats ds ON ds.depositor_id = dep.id
            LEFT JOIN interest_stats is2 ON is2.depositor_id = dep.id
            LEFT JOIN transaction_stats ts ON ts.depositor_id = dep.id
            ORDER BY total_deposit_amount DESC, dep.id ASC
            """,
            (
                INCOME_OPERATION_TYPES[0],
                INCOME_OPERATION_TYPES[1],
                EXPENSE_OPERATION_TYPES[0],
                EXPENSE_OPERATION_TYPES[1],
            ),
        ).fetchall()

        if not rows:
            return empty_data("Список вкладчиков пуст.", data=[])

        return success(
            [dict(row) for row in rows],
            "Сводка по вкладчикам сформирована.",
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            exc,
            fallback_data=[],
            default_message="Не удалось получить сводку по вкладчикам.",
        )
