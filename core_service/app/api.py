import hashlib
from flask import jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from core_service.app.about_data import load_about_data
from core_service.app.db import get_db
from datetime import datetime

def register_api_routes(app):
    @app.route("/api/hash/<string:value>", methods=["GET"], endpoint="api_hash")
    def api_hash(value):
        result = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return jsonify({"request": value, "result": result })

    @app.route("/api/about", methods=["GET"], endpoint="api_about")
    def api_about():
        return jsonify(load_about_data())

    @app.route("/api/me", methods=["GET"])
    @jwt_required()
    def api_me():
        user_id = int(get_jwt_identity())
        db = get_db()
        user = db.execute(
            """
            SELECT id, user_name, email, role, is_active
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            abort(404)

        return jsonify(dict(user))

    @app.route("/api/dashboard", methods=["GET"], endpoint="api_dashboard")
    def api_dashboard():
        db = get_db()

        kpi_row = db.execute(
            """
            SELECT
                COUNT(DISTINCT d.depositor_id) AS depositors_count,
                COUNT(d.id) AS deposits_count,
                SUM(CASE WHEN d.status = 'active' THEN 1 ELSE 0 END) AS active_deposits_count,
                COALESCE(SUM(d.amount), 0.0) AS portfolio_amount
            FROM deposits d
            """
        ).fetchone()

        interest_row = db.execute(
            """
            SELECT COALESCE(SUM(ia.amount), 0.0) AS accrued_interest_total
            FROM interest_accruals ia
            """
        ).fetchone()

        status_rows = db.execute(
            """
            SELECT d.status, COUNT(*) AS count
            FROM deposits d
            GROUP BY d.status
            ORDER BY count DESC
            """
        ).fetchall()

        currency_rows = db.execute(
            """
            SELECT d.currency, COALESCE(SUM(d.amount), 0.0) AS amount
            FROM deposits d
            GROUP BY d.currency
            ORDER BY amount DESC
            """
        ).fetchall()

        top_rows = db.execute(
            """
            SELECT
                dep.id AS depositor_id,
                TRIM(dep.lastname || ' ' || dep.firstname || ' ' || COALESCE(dep.middlename, '')) AS full_name,
                COUNT(d.id) AS deposits_count,
                COALESCE(SUM(d.amount), 0.0) AS total_deposit_amount
            FROM depositors dep
            JOIN deposits d ON d.depositor_id = dep.id
            GROUP BY dep.id, dep.lastname, dep.firstname, dep.middlename
            ORDER BY total_deposit_amount DESC, dep.id ASC
            LIMIT 10
            """
        ).fetchall()

        now = datetime.now()
        cash_flow_6m = []

        for i in range(5, -1, -1):
            year = now.year
            month = now.month - i

            while month <= 0:
                month += 12
                year -= 1

            start = f"{year}-{month:02d}-01"
            if month == 12:
                end = f"{year + 1}-01-01"
            else:
                end = f"{year}-{month + 1:02d}-01"

            rows = db.execute(
                """
                SELECT operation_type, COALESCE(SUM(amount), 0.0) AS total
                FROM transactions
                WHERE operation_date >= ? AND operation_date < ?
                GROUP BY operation_type
                """,
                (start, end),
            ).fetchall()

            income = sum(
                float(r["total"]) for r in rows
                if r["operation_type"] in ("deposit_open", "deposit_topup")
            )
            expense = sum(
                float(r["total"]) for r in rows
                if r["operation_type"] in ("deposit_return", "interest_payment")
            )

            cash_flow_6m.append({
                "month": f"{year}-{month:02d}",
                "income": income,
                "expense": expense,
                "balance": income - expense,
            })

        return jsonify({
            "ok": True,
            "data": {
                "generated_at": now.strftime("%d.%m.%Y %H:%M:%S"),
                "kpi": {
                    "depositors_count": kpi_row["depositors_count"] or 0,
                    "deposits_count": kpi_row["deposits_count"] or 0,
                    "active_deposits_count": kpi_row["active_deposits_count"] or 0,
                    "portfolio_amount": float(kpi_row["portfolio_amount"] or 0.0),
                    "accrued_interest_total": float(interest_row["accrued_interest_total"] or 0.0),
                },
                "deposits_by_status": [
                    {"status": row["status"], "count": row["count"]}
                    for row in status_rows
                ],
                "deposits_by_currency": [
                    {"currency": row["currency"], "amount": float(row["amount"])}
                    for row in currency_rows
                ],
                "cash_flow_6m": cash_flow_6m,
                "top_depositors": [
                    {
                        "depositor_id": row["depositor_id"],
                        "full_name": row["full_name"],
                        "deposits_count": row["deposits_count"],
                        "total_deposit_amount": float(row["total_deposit_amount"]),
                    }
                    for row in top_rows
                ],
            },
            "message": "Dashboard loaded.",
        })

    @app.route("/api/depositors", methods=["GET"])
    @jwt_required()
    def api_depositors():
        db = get_db()
        rows = db.execute(
            """
            SELECT
                id,
                last_name,
                first_name,
                middle_name,
                passport_series,
                passport_number,
                phone,
                email,
                address
            FROM depositors
            ORDER BY id DESC
            """
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    @app.route("/api/deposits", methods=["GET"])
    @jwt_required()
    def api_deposits():
        db = get_db()
        rows = db.execute(
            """
            SELECT
                id,
                depositor_id,
                deposit_type,
                amount,
                interest_rate,
                start_date,
                end_date,
                capitalization,
                auto_renewal,
                status,
                currency
            FROM deposits
            ORDER BY id DESC
            """
        ).fetchall()

        return jsonify([dict(row) for row in rows])
