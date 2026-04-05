from __future__ import annotations
import sqlite3
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from supporting_service.constants import ( EXPENSE_OPERATION_TYPES, INCOME_OPERATION_TYPES, MODULE_REPORTS, SERVICE_NAME, TWO_PLACES )
from supporting_service.db import get_connection
from supporting_service.utils.fallbacks import exception_fallback, success

def normalize_money(value: Any) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def empty_cash_flow(start_dt=None, end_dt=None):
    return {
        "start": start_dt.isoformat(sep=" ") if start_dt else None,
        "end": end_dt.isoformat(sep=" ") if end_dt else None,
        "income": "0.00",
        "expense": "0.00",
        "balance": "0.00",
    }

def get_cash_flow_by_period(
    start_dt: datetime,
    end_dt: datetime,
) -> dict[str, Any]:
    conn = get_connection()
    try:
        cursor = conn.cursor()

        sql = """
        SELECT
            t.operation_type,
            SUM(t.amount) AS total_amount
        FROM transactions t
        WHERE t.operation_date >= ?
          AND t.operation_date < ?
        GROUP BY t.operation_type
        """
        rows = cursor.execute(
            sql,
            (start_dt.date().isoformat(), end_dt.date().isoformat()),
        ).fetchall()

        income = Decimal("0.00")
        expense = Decimal("0.00")

        for row in rows:
            amount = normalize_money(row["total_amount"])
            if row["operation_type"] in INCOME_OPERATION_TYPES:
                income += amount
            elif row["operation_type"] in EXPENSE_OPERATION_TYPES:
                expense += amount

        balance = income - expense

        data = {
            "start": start_dt.isoformat(sep=" "),
            "end": end_dt.isoformat(sep=" "),
            "income": str(income),
            "expense": str(expense),
            "balance": str(balance),
        }
        return success(
            service=SERVICE_NAME,
            module=MODULE_REPORTS,
            data=data,
        )
    except sqlite3.Error as exc:
        return exception_fallback(
            service=SERVICE_NAME,
            module=MODULE_REPORTS,
            exception=exc,
            fallback_data=empty_cash_flow(start_dt, end_dt),
            default_message="Ошибка при расчете движения денежных средств.",
        )
    finally:
        conn.close()

def get_today_cash_flow():
    start_dt = datetime.combine(date.today(), datetime.min.time())
    end_dt = datetime.combine(date.today(), datetime.max.time())
    return get_cash_flow_by_period(start_dt, end_dt)

def get_month_cash_flow(year, month):
    start_dt = datetime(year, month, 1)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_year_cash_flow(year):
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    return get_cash_flow_by_period(start_dt, end_dt)

def get_reports_snapshot():
    today = get_today_cash_flow()
    now = datetime.now()
    month = get_month_cash_flow(now.year, now.month)
    year = get_year_cash_flow(now.year)

    return success(
        SERVICE_NAME,
        MODULE_REPORTS,
        {
            "today": today["data"],
            "month": month["data"],
            "year": year["data"],
        },
        message="Сводный отчет сформирован.",
    )
