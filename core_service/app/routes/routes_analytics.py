import logging
from datetime import datetime
from flask import render_template
from flask_login import login_required
from core_service.app.routes.routes_helpers import flash_service_message
from core_service.app.services.interest_service import (get_deposits_for_return_tomorrow, get_month_return_plan)
from core_service.app.services.report_service import (get_all_depositors_summary, get_five_year_cash_flow, get_month_cash_flow, get_today_cash_flow, get_year_cash_flow)

logger = logging.getLogger(__name__)

def register_analytics_routes(app):
    @app.route("/dashboard", endpoint="dashboard")
    @login_required
    def dashboard():
        logger.debug("Dashboard page requested")
        return render_template("dashboard.html")

    @app.route("/reports", endpoint="reports")
    @login_required
    def reports():
        now = datetime.now()
        today_result = get_today_cash_flow()
        month_result = get_month_cash_flow(now.year, now.month)
        year_result = get_year_cash_flow(now.year)
        five_year_result = get_five_year_cash_flow(now.year - 4)
        summary_result = get_all_depositors_summary()

        for result in (
            today_result,
            month_result,
            year_result,
            five_year_result,
            summary_result,
        ):
            flash_service_message(result)

        logger.debug("Reports page prepared for year=%s month=%s", now.year, now.month)
        return render_template(
            "reports.html",
            today_report=today_result.get("data") or {"income": "0.00", "expense": "0.00", "balance": "0.00"},
            month_report=month_result.get("data") or {"income": "0.00", "expense": "0.00", "balance": "0.00"},
            year_report=year_result.get("data") or {"income": "0.00", "expense": "0.00", "balance": "0.00"},
            five_year_report=five_year_result.get("data") or {"income": "0.00", "expense": "0.00", "balance": "0.00"},
            depositors_summary=summary_result.get("data") or [],
        )

    @app.route("/return-plan", endpoint="return_plan")
    @login_required
    def return_plan():
        now = datetime.now()
        tomorrow_result = get_deposits_for_return_tomorrow()
        month_plan_result = get_month_return_plan(now.year, now.month)
        flash_service_message(tomorrow_result)
        flash_service_message(month_plan_result)
        month_plan_data = month_plan_result.get("data") or {"items": [], "total_sum": "0.00"}

        logger.debug("Return plan page prepared for year=%s month=%s", now.year, now.month)
        return render_template(
            "return_plan.html",
            tomorrow_items=tomorrow_result.get("data") or [],
            month_plan=month_plan_data,
            month_plan_items=month_plan_data.get("items", []),
        )
