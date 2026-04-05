import logging
import sqlite3
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from core_service.app.queries.list_queries import search_deposits
from core_service.app.services.deposit_service import (create_deposit as create_deposit_service, delete_deposit as delete_deposit_service, get_deposit_for_edit, topup_deposit as topup_deposit_service, update_deposit as update_deposit_service )
from core_service.app.services.interest_service import create_accrual_for_deposit
from core_service.app.routes.routes_helpers import (empty_paginated_deposits, flash_service_message, load_depositors_for_select, validate_deposit_form )
from core_service.app.constants import CURRENCIES, DEPOSIT_STATUSES, CurrencyCode, DepositStatus

logger = logging.getLogger(__name__)

def register_deposit_routes(app):
    @app.route("/deposits", endpoint="deposits")
    @login_required
    def deposits():
        try:
            result = search_deposits(
                search=request.args.get("search"),
                status=request.args.get("status"),
                currency=request.args.get("currency"),
                min_amount=request.args.get("min_amount"),
                max_amount=request.args.get("max_amount"),
                sort_by=request.args.get("sort_by", "id"),
                sort_order=request.args.get("sort_order", "desc"),
                page=request.args.get("page", 1),
                page_size=request.args.get("page_size", 20),
            )
        except sqlite3.Error:
            logger.exception(
                "Failed to load deposits list: "
                "search=%r status=%r currency=%r min_amount=%r max_amount=%r "
                "sort_by=%r sort_order=%r",
                request.args.get("search"),
                request.args.get("status"),
                request.args.get("currency"),
                request.args.get("min_amount"),
                request.args.get("max_amount"),
                request.args.get("sort_by", "id"),
                request.args.get("sort_order", "desc"),
            )
            flash("Не удалось загрузить список вкладов.", "error")
            result = empty_paginated_deposits()

        return render_template(
            "deposits.html",
            deposits=result["items"],
            pagination=result["pagination"],
            filters=result["filters"],
            sorting=result["sorting"],
        )

    @app.route("/deposits/create", methods=["GET", "POST"], endpoint="create_deposit")
    @login_required
    def create_deposit():
        depositors = load_depositors_for_select()

        template_ctx = {
            "depositors": depositors,
            "currencyoptions": CURRENCIES,
            "statusoptions": DEPOSIT_STATUSES,
            "defaultcurrency": CurrencyCode.RUB.value,
            "defaultstatus": DepositStatus.ACTIVE.value,
        }

        if request.method == "POST":
            payload, error = validate_deposit_form(
                request.form,
                opened_by_user_id=current_user.id,
            )
            if error:
                flash(error, "error")
                return render_template("create_deposit.html", **template_ctx)

            service_result = create_deposit_service(payload)
            flash(
                service_result["message"],
                "success" if service_result["ok"] else "error",
            )

            if service_result["ok"]:
                return redirect(url_for("deposits"))
        return render_template("create_deposit.html", **template_ctx)

    def _render_edit_deposit_form(deposit_id: int):
        service_result = get_deposit_for_edit(deposit_id)
        if not service_result["ok"] or not service_result["data"]:
            flash(service_result["message"], "error")
            return redirect(url_for("deposits"))

        depositors = load_depositors_for_select()
        return render_template(
            "edit_deposit.html",
            deposit=service_result["data"],
            depositors=depositors,
            currency_options=CURRENCIES,
            status_options=DEPOSIT_STATUSES,
        )

    def _render_topup_deposit_form(deposit_id: int):
        service_result = get_deposit_for_edit(deposit_id)
        if not service_result["ok"] or not service_result["data"]:
            flash(service_result["message"], "error")
            return redirect(url_for("deposits"))

        return render_template(
            "topup_deposit.html",
            deposit=service_result["data"],
        )

    @app.route("/deposits/edit/<int:deposit_id>", methods=["GET", "POST"], endpoint="edit_deposit")
    @login_required
    def edit_deposit(deposit_id: int):
        if request.method == "POST":
            payload, error = validate_deposit_form(
                request.form,
                opened_by_user_id=current_user.id,
            )
            if error:
                flash(error, "error")
                return _render_edit_deposit_form(deposit_id)

            service_result = update_deposit_service(deposit_id, payload)
            flash(
                service_result["message"],
                "success" if service_result["ok"] else "error",
            )

            if service_result["ok"]:
                return redirect(url_for("deposits"))
            return _render_edit_deposit_form(deposit_id)
        return _render_edit_deposit_form(deposit_id)

    @app.route("/deposits/topup/<int:deposit_id>", methods=["GET", "POST"], endpoint="topup_deposit" )
    @login_required
    def topup_deposit(deposit_id: int):
        if request.method == "POST":
            raw_amount = (request.form.get("amount") or "").strip()
            try:
                amount = float(raw_amount)
            except ValueError:
                flash("Введите корректную сумму пополнения.", "error")
                return _render_topup_deposit_form(deposit_id)

            service_result = topup_deposit_service(deposit_id, amount)
            flash_service_message(service_result)

            if service_result["ok"]:
                return redirect(url_for("deposits"))
            return _render_topup_deposit_form(deposit_id)
        return _render_topup_deposit_form(deposit_id)

    @app.route("/deposits/delete/<int:deposit_id>", methods=["POST"], endpoint="delete_deposit" )
    @login_required
    def delete_deposit(deposit_id: int):
        service_result = delete_deposit_service(deposit_id)
        flash(
            service_result["message"],
            "success" if service_result["ok"] else "error",
        )
        return redirect(url_for("deposits"))

    @app.route("/deposits/accrue/<int:deposit_id>", methods=["POST"], endpoint="accrue_deposit" )
    @login_required
    def accrue_deposit(deposit_id: int):
        result = create_accrual_for_deposit(deposit_id)
        flash_service_message(result)
        return redirect(url_for("deposits"))
