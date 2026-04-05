import logging
import sqlite3
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from core_service.app.queries.list_queries import search_depositors
from core_service.app.services.depositor_service import (create_depositor as create_depositor_service, delete_depositor as delete_depositor_service, get_depositor_for_edit, update_depositor as update_depositor_service )
from core_service.app.routes.routes_helpers import ( empty_paginated_depositors, validate_depositor_form)

logger = logging.getLogger(__name__)

def register_depositor_routes(app):
    @app.route("/depositors", endpoint="depositors")
    @login_required
    def depositors():
        try:
            result = search_depositors(
                search=request.args.get("search"),
                phone=request.args.get("phone"),
                email=request.args.get("email"),
                sort_by=request.args.get("sort_by", request.args.get("sortby", "id")),
                sort_order=request.args.get("sort_order", request.args.get("sortorder", "desc")),
                page=request.args.get("page", 1),
                page_size=request.args.get("page_size", request.args.get("pagesize", 20)),
            )
        except sqlite3.Error:
            logger.exception(
                "Failed to load depositors list search=%r phone=%r email=%r sortby=%r sortorder=%r",
                request.args.get("search"),
                request.args.get("phone"),
                request.args.get("email"),
                request.args.get("sortby", "id"),
                request.args.get("sortorder", "desc"),
            )
            flash("Не удалось загрузить список вкладчиков.", "error")
            result = empty_paginated_depositors()

        return render_template(
            "depositors.html",
            depositors=result["items"],
            pagination=result["pagination"],
            filters=result["filters"],
            sorting=result["sorting"],
        )

    @app.route("/depositors/create", methods=["GET", "POST"], endpoint="createdepositor")
    @login_required
    def createdepositor():
        if request.method == "POST":
            payload, error = validate_depositor_form(
                request.form,
                created_by_user_id=current_user.id,
            )
            if error:
                flash(error, "error")
                return render_template("createdepositor.html")

            service_result = create_depositor_service(
                payload=payload,
                created_by_user_id=current_user.id,
            )
            flash(
                service_result["message"],
                "success" if service_result.get("ok") else "error",
            )
            if service_result.get("ok"):
                return redirect(url_for("depositors"))

        return render_template("createdepositor.html")

    def render_edit_depositor_form(depositor_id: int):
        service_result = get_depositor_for_edit(depositor_id)
        if not service_result.get("ok") or not service_result.get("data"):
            flash(service_result.get("message", "Не удалось загрузить вкладчика."), "error")
            return redirect(url_for("depositors"))

        return render_template(
            "editdepositor.html",
            depositor=service_result["data"],
        )

    @app.route("/depositors/edit/<int:depositor_id>", methods=["GET", "POST"], endpoint="editdepositor" )
    @login_required
    def editdepositor(depositor_id: int):
        if request.method == "POST":
            payload, error = validate_depositor_form(
                request.form,
                created_by_user_id=current_user.id,
            )
            if error:
                flash(error, "error")
                return render_edit_depositor_form(depositor_id)

            service_result = update_depositor_service(
                depositor_id,
                {
                    "lastname": payload.last_name,
                    "firstname": payload.first_name,
                    "middlename": payload.middle_name,
                    "passportseries": payload.passport_series,
                    "passportnumber": payload.passport_number,
                    "issuedby": payload.issued_by,
                    "phone": payload.phone,
                    "email": payload.email,
                    "address": payload.address,
                },
            )
            flash(
                service_result["message"],
                "success" if service_result.get("ok") else "error",
            )
            if service_result.get("ok"):
                return redirect(url_for("depositors"))
            return render_edit_depositor_form(depositor_id)
        return render_edit_depositor_form(depositor_id)

    @app.route("/depositors/delete/<int:depositor_id>", methods=["POST"], endpoint="deletedepositor" )
    @login_required
    def deletedepositor(depositor_id: int):
        service_result = delete_depositor_service(depositor_id)
        flash(
            service_result["message"],
            "success" if service_result.get("ok") else "error",
        )
        return redirect(url_for("depositors"))
