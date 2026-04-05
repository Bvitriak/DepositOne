from __future__ import annotations
import logging
from datetime import date, datetime, timedelta
from typing import Any
from supporting_service.constants import MODULE_ANALYTICS, SERVICE_NAME
from supporting_service.db import get_connection
from supporting_service.utils.fallbacks import empty_data, exception_fallback, success

logger = logging.getLogger(__name__)

def get_dashboard_data() -> dict[str, Any]:
    conn = None
    try:
        logger.debug("Dashboard data request started")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(DISTINCT d.depositor_id)          AS depositors_count,
                COUNT(d.id)                             AS deposits_count,
                SUM(CASE WHEN d.status = 'active' THEN 1 ELSE 0 END) AS active_deposits_count,
                COALESCE(SUM(d.amount), 0.0)            AS portfolio_amount
            FROM deposits d
        """)
        kpi_row = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(ia.amount), 0.0) AS accrued_interest_total
            FROM interest_accruals ia
        """)
        interest_row = cursor.fetchone()

        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM deposits
            GROUP BY status
            ORDER BY count DESC
        """)
        status_rows = cursor.fetchall()

        cursor.execute("""
            SELECT currency, COALESCE(SUM(amount), 0.0) AS amount
            FROM deposits
            GROUP BY currency
            ORDER BY amount DESC
        """)
        currency_rows = cursor.fetchall()

        today = date.today()
        months = []
        for i in range(5, -1, -1):
            if today.month - i <= 0:
                year = today.year - 1
                month = today.month - i + 12
            else:
                year = today.year
                month = today.month - i
            months.append((year, month))

        cash_flow_6m = []
        for year, month in months:
            start = f"{year}-{month:02d}-01"
            if month == 12:
                end = f"{year+1}-01-01"
            else:
                end = f"{year}-{month+1:02d}-01"

            cursor.execute("""
                SELECT operation_type, COALESCE(SUM(amount), 0.0) AS total
                FROM transactions
                WHERE operation_date >= ? AND operation_date < ?
                GROUP BY operation_type
            """, (start, end))
            rows = cursor.fetchall()
            income = sum(r["total"] for r in rows if r["operation_type"] in ("deposit_open", "deposit_topup"))
            expense = sum(r["total"] for r in rows if r["operation_type"] in ("deposit_return", "interest_payment"))
            cash_flow_6m.append({
                "month": f"{year}-{month:02d}",
                "income": float(income),
                "expense": float(expense),
                "balance": float(income - expense),
            })

        cursor.execute("""
            SELECT
                dep.id           AS depositor_id,
                dep.last_name    AS last_name,
                dep.first_name   AS first_name,
                dep.middle_name  AS middle_name,
                COUNT(d.id)      AS deposits_count,
                COALESCE(SUM(d.amount), 0.0) AS total_deposit_amount
            FROM depositors dep
            JOIN deposits d ON d.depositor_id = dep.id
            GROUP BY dep.id
            ORDER BY total_deposit_amount DESC
            LIMIT 10
        """)
        top_rows = cursor.fetchall()

        data = {
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "kpi": {
                "depositors_count":       kpi_row["depositors_count"] or 0,
                "deposits_count":         kpi_row["deposits_count"] or 0,
                "active_deposits_count":  kpi_row["active_deposits_count"] or 0,
                "portfolio_amount":       float(kpi_row["portfolio_amount"] or 0.0),
                "accrued_interest_total": float(interest_row["accrued_interest_total"] or 0.0),
            },
            "deposits_by_status": [
                {"status": r["status"], "count": r["count"]}
                for r in status_rows
            ],
            "deposits_by_currency": [
                {"currency": r["currency"], "amount": float(r["amount"])}
                for r in currency_rows
            ],
            "cash_flow_6m": cash_flow_6m,
            "top_depositors": [
                {
                    "depositor_id": r["depositor_id"],
                    "full_name": f"{r['last_name']} {r['first_name']} {r['middle_name'] or ''}".strip(),
                    "deposits_count": r["deposits_count"],
                    "total_deposit_amount": float(r["total_deposit_amount"]),
                }
                for r in top_rows
            ],
        }

        return success(SERVICE_NAME, MODULE_ANALYTICS, data=data, message="Dashboard загружен.")

    except Exception as exc:
        logger.exception("Dashboard data load failed")
        return exception_fallback(SERVICE_NAME, MODULE_ANALYTICS, exc, default_message="Ошибка загрузки dashboard.")
    finally:
        if conn is not None:
            conn.close

def get_dashboard_metrics() -> dict[str, Any]:
    return get_dashboard_data()

def get_returns_tomorrow() -> dict[str, Any]:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        tomorrow = date.today() + timedelta(days=1)
        cursor.execute(
            """
            SELECT id, depositor_id, amount, interest_rate, end_date, status
            FROM deposits
            WHERE end_date = ?
            ORDER BY id ASC
            """,
            (tomorrow.isoformat(),),
        )
        rows = cursor.fetchall()

        items = [dict(row) for row in rows]
        if not items:
            return empty_data(
                SERVICE_NAME,
                MODULE_ANALYTICS,
                "На завтра возвратов нет.",
                data=[],
            )

        return success(
            SERVICE_NAME,
            MODULE_ANALYTICS,
            data=items,
            message="Список возвратов на завтра сформирован.",
        )
    except Exception as exc:
        return exception_fallback(
            SERVICE_NAME,
            MODULE_ANALYTICS,
            exc,
            fallback_data=[],
            default_message="Не удалось получить список возвратов на завтра.",
        )
    finally:
        if conn is not None:
            conn.close()


def get_analytics_snapshot() -> dict[str, Any]:
    dashboard = get_dashboard_data()
    returns_tomorrow = get_returns_tomorrow()

    return success(
        SERVICE_NAME,
        MODULE_ANALYTICS,
        data={
            "dashboard": dashboard.get("data"),
            "returns_tomorrow": returns_tomorrow.get("data"),
        },
        message="Сводная аналитика сформирована.",
    )

def get_deposits_list(
    search: str | None = None,
    status: str | None = None,
    currency: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        allowed_sort_fields = {
            "id": "d.id",
            "amount": "d.amount",
            "interest_rate": "d.interest_rate",
            "start_date": "d.start_date",
            "end_date": "d.end_date",
            "status": "d.status",
            "deposit_type": "d.deposit_type",
        }
        sort_column = allowed_sort_fields.get(sort_by, "d.id")
        direction = "ASC" if str(sort_order).lower() == "asc" else "DESC"

        where = []
        params: list[Any] = []

        if search:
            where.append("(lower(d.deposit_type) LIKE lower(?) OR CAST(d.id AS TEXT) LIKE ?)")
            term = f"%{search.strip()}%"
            params.extend([term, term])

        if status:
            where.append("d.status = ?")
            params.append(status)

        if currency:
            where.append("d.currency = ?")
            params.append(currency)

        if min_amount is not None:
            where.append("CAST(d.amount AS REAL) >= ?")
            params.append(min_amount)

        if max_amount is not None:
            where.append("CAST(d.amount AS REAL) <= ?")
            params.append(max_amount)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        offset = max(page - 1, 0) * page_size

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM deposits d
            {where_sql}
        """
        data_sql = f"""
            SELECT
                d.id,
                d.depositor_id,
                d.deposit_type,
                d.amount,
                d.interest_rate,
                d.currency,
                d.start_date,
                d.end_date,
                d.status,
                d.capitalization,
                d.auto_renewal
            FROM deposits d
            {where_sql}
            ORDER BY {sort_column} {direction}, d.id DESC
            LIMIT ? OFFSET ?
        """

        total = cursor.execute(count_sql, params).fetchone()["total"]
        rows = cursor.execute(data_sql, [*params, page_size, offset]).fetchall()

        return success(
            SERVICE_NAME,
            MODULE_ANALYTICS,
            data={
                "items": [dict(row) for row in rows],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size if total else 0,
                    "has_prev": page > 1,
                    "has_next": page * page_size < total,
                },
                "filters": {
                    "search": search or "",
                    "status": status or "",
                    "currency": currency or "",
                    "min_amount": min_amount,
                    "max_amount": max_amount,
                },
                "sorting": {
                    "sort_by": sort_by,
                    "sort_order": direction.lower(),
                },
            },
            message="Список вкладов сформирован.",
        )
    except Exception as exc:
        return exception_fallback(
            SERVICE_NAME,
            MODULE_ANALYTICS,
            exc,
            fallback_data={
                "items": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "total_pages": 0,
                    "has_prev": False,
                    "has_next": False,
                },
                "filters": {
                    "search": search or "",
                    "status": status or "",
                    "currency": currency or "",
                    "min_amount": min_amount,
                    "max_amount": max_amount,
                },
                "sorting": {
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                },
            },
            default_message="Не удалось получить список вкладов.",
        )
    finally:
        if conn is not None:
            conn.close()
