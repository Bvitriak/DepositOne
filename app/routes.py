from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app.db import db
from app.models.depositor import Depositor
from app.models.deposit import Deposit
from app.models.contract import Contract
from app.models.transaction import Transaction
from app.services.contractService import create_contract
from app.services.interestService import (
    create_accrual_for_deposit,
    get_deposits_for_return_tomorrow,
    get_month_return_plan,
)
from app.services.reportService import (
    get_today_cash_flow,
    get_month_cash_flow,
    get_year_cash_flow,
    get_five_year_cash_flow,
    get_all_depositors_summary,
)

def register_routes(app):
    @app.route("/")
    def index():
        depositors_count = Depositor.query.count()
        deposits_count = Deposit.query.count()
        contracts_count = Contract.query.count()
        transactions_count = Transaction.query.count()

        return render_template(
            "index.html",
            depositors_count=depositors_count,
            deposits_count=deposits_count,
            contracts_count=contracts_count,
            transactions_count=transactions_count,
        )

    @app.route("/depositors")
    def depositors():
        items = Depositor.query.order_by(Depositor.id.desc()).all()
        return render_template("depositors.html", depositors=items)

    @app.route("/depositors/create", methods=["GET", "POST"], endpoint="createDepositor")
    def create_depositor():
        if request.method == "POST":
            depositor = Depositor(
                last_name=request.form.get("last_name"),
                first_name=request.form.get("first_name"),
                middle_name=request.form.get("middle_name"),
                passport_series=request.form.get("passport_series"),
                passport_number=request.form.get("passport_number"),
                issued_by=request.form.get("issued_by"),
                address=request.form.get("address"),
                phone=request.form.get("phone"),
                email=request.form.get("email"),
            )

            db.session.add(depositor)
            db.session.commit()

            flash("Вкладчик успешно добавлен", "success")
            return redirect(url_for("depositors"))

        return render_template("createDepositor.html")

    @app.route("/deposits")
    def deposits():
        items = Deposit.query.order_by(Deposit.id.desc()).all()
        depositors_list = Depositor.query.all()
        return render_template("deposits.html", deposits=items, depositors=depositors_list)

    @app.route("/deposits/create", methods=["GET", "POST"], endpoint="createDeposit")
    def create_deposit():
        if request.method == "POST":
            depositor_id = int(request.form.get("depositor_id"))
            amount = request.form.get("amount")
            interest_rate = request.form.get("interest_rate")
            start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
            term_months = int(request.form.get("term_months"))

            deposit = Deposit(
                depositor_id=depositor_id,
                deposit_type=request.form.get("deposit_type"),
                amount=amount,
                interest_rate=interest_rate,
                start_date=start_date,
                end_date=end_date,
                term_months=term_months,
                capitalization=True if request.form.get("capitalization") == "on" else False,
                auto_renewal=True if request.form.get("auto_renewal") == "on" else False,
                status="active",
                currency=request.form.get("currency") or "RUB",
            )

            db.session.add(deposit)
            db.session.commit()

            transaction = Transaction(
                deposit_id=deposit.id,
                operation_type="deposit_open",
                amount=amount,
                description="Открытие вклада",
                cashier_name="Оператор банка",
            )
            db.session.add(transaction)
            db.session.commit()

            flash("Вклад успешно открыт", "success")
            return redirect(url_for("deposits"))

        depositors_list = Depositor.query.order_by(Depositor.last_name.asc()).all()
        return render_template("createDeposit.html", depositors=depositors_list)

    @app.route("/contracts")
    def contracts():
        items = Contract.query.order_by(Contract.id.desc()).all()
        return render_template("contracts.html", contracts=items)

    @app.route("/contracts/create/<int:deposit_id>", methods=["GET", "POST"], endpoint="createContract")
    def create_contract_route(deposit_id):
        deposit = Deposit.query.get_or_404(deposit_id)

        if request.method == "POST":
            contract = create_contract(
                depositor_id=deposit.depositor_id,
                deposit_id=deposit.id,
                term_description=request.form.get("term_description"),
                special_conditions=request.form.get("special_conditions"),
            )

            flash(f"Договор {contract.contract_number} создан", "success")
            return redirect(url_for("contracts"))

        return render_template("createContract.html", deposit=deposit)

    @app.route("/accruals/create/<int:deposit_id>", methods=["POST"], endpoint="createAccrual")
    def create_accrual(deposit_id):
        deposit = Deposit.query.get_or_404(deposit_id)
        accrual = create_accrual_for_deposit(deposit)

        flash(f"Начисление процентов создано: {accrual.interest_amount}", "success")
        return redirect(url_for("deposits"))

    @app.route("/reports")
    def reports():
        today_report = get_today_cash_flow()

        now = datetime.now()
        month_report = get_month_cash_flow(now.year, now.month)
        year_report = get_year_cash_flow(now.year)
        five_year_report = get_five_year_cash_flow(now.year - 4)
        depositors_summary = get_all_depositors_summary()

        return render_template(
            "reports.html",
            today_report=today_report,
            month_report=month_report,
            year_report=year_report,
            five_year_report=five_year_report,
            depositors_summary=depositors_summary,
        )

    @app.route("/return-plan", endpoint="returnPlan")
    def return_plan():
        tomorrow_items = get_deposits_for_return_tomorrow()

        now = datetime.now()
        month_plan = get_month_return_plan(now.year, now.month)

        return render_template(
            "returnPlan.html",
            tomorrow_items=tomorrow_items,
            month_plan=month_plan,
        )
