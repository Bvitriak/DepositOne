import logging
import sqlite3
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from core_service.app.queries.list_queries import search_contracts
from core_service.app.routes.routes_helpers import (empty_paginated_contracts, flash_service_message, get_row_or_404)
from core_service.app.services.contract_service import create_contract

logger = logging.getLogger(__name__)

def register_contract_routes(app):
    @app.route("/contracts", endpoint="contracts")
    @login_required
    def contracts():
        try:
            result = search_contracts(
                search=request.args.get("search"),
                is_signed=request.args.get("is_signed", request.args.get("issigned")),
                sort_by=request.args.get("sort_by", request.args.get("sortby", "id")),
                sort_order=request.args.get("sort_order", request.args.get("sortorder", "desc")),
                page=request.args.get("page", 1),
                page_size=request.args.get("page_size", request.args.get("pagesize", 20)),
            )
        except sqlite3.Error as exc:
            logger.exception(
                "Failed to load contracts list: search=%r is_signed=%r sort_by=%r sort_order=%r error=%s",
                request.args.get("search"),
                request.args.get("is_signed", request.args.get("issigned")),
                request.args.get("sort_by", request.args.get("sortby", "id")),
                request.args.get("sort_order", request.args.get("sortorder", "desc")),
                exc,
            )
            flash("Не удалось загрузить список договоров.", "error")
            result = empty_paginated_contracts()

        return render_template(
            "contracts.html",
            contracts=result["items"],
            pagination=result["pagination"],
            filters=result["filters"],
            sorting=result["sorting"],
        )

    @app.route("/contracts/create/<int:deposit_id>", methods=["GET", "POST"], endpoint="create_contract")
    @login_required
    def create_contract_view(deposit_id):
        deposit = get_row_or_404(
            """
            SELECT
                d.id,
                d.amount,
                d.interest_rate,
                d.start_date,
                d.end_date,
                dep.lastname,
                dep.firstname,
                dep.middlename
            FROM deposits d
            JOIN depositors dep ON dep.id = d.depositor_id
            WHERE d.id = ?
            """,
            (deposit_id,),
        )

        if request.method == "POST":
            logger.info(
                "Create contract requested for deposit_id=%s by user_id=%s",
                deposit_id,
                current_user.id,
            )
            result = create_contract(
                deposit_id=deposit_id,
                created_by_user_id=current_user.id,
                term_description=request.form.get("term_description"),
                special_conditions=request.form.get("special_conditions"),
            )
            flash_service_message(result)

            if result.get("ok"):
                logger.info("Contract created successfully for deposit_id=%s", deposit_id)
                return redirect(url_for("contracts"))

            logger.warning(
                "Contract creation failed for deposit_id=%s: %s",
                deposit_id,
                result.get("message"),
            )

        return render_template("create_contract.html", deposit=deposit)
