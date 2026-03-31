from datetime import date
from app.db import db
from app.models.contract import Contract
from app.models.depositor import Depositor
from app.models.deposit import Deposit

def generate_contract_number():
    today = date.today().strftime("%Y%m%d")
    count_today = Contract.query.filter(Contract.contract_date == date.today()).count() + 1
    return f"DEP-{today}-{count_today:04d}"

def create_contract(depositor_id, deposit_id, term_description=None, special_conditions=None):
    contract = Contract(
        contract_number=generate_contract_number(),
        contract_date=date.today(),
        depositor_id=depositor_id,
        deposit_id=deposit_id,
        term_description=term_description,
        special_conditions=special_conditions,
        is_signed=True
    )

    db.session.add(contract)
    db.session.commit()

    return contract

def get_contract_data(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    depositor = Depositor.query.get(contract.depositor_id)
    deposit = Deposit.query.get(contract.deposit_id)

    return {
        "contract_number": contract.contract_number,
        "contract_date": contract.contract_date,
        "depositor_full_name": f"{depositor.last_name} {depositor.first_name} {depositor.middle_name or ''}".strip(),
        "passport_series": depositor.passport_series,
        "passport_number": depositor.passport_number,
        "address": depositor.address,
        "phone": depositor.phone,
        "deposit_type": deposit.deposit_type,
        "amount": deposit.amount,
        "interest_rate": deposit.interest_rate,
        "start_date": deposit.start_date,
        "end_date": deposit.end_date,
        "term_months": deposit.term_months,
        "capitalization": deposit.capitalization,
        "auto_renewal": deposit.auto_renewal,
        "special_conditions": contract.special_conditions
    }

def render_contract_text(contract_id):
    data = get_contract_data(contract_id)

    text = f'''
Договор Банкосвкого Вклада № {data["contract_number"]}
Дата заключения: {data["contract_date"]}

Вкладчик: {data["depositor_full_name"]}
Паспорт: {data["passport_series"]} {data["passport_number"]}
Адрес: {data["address"]}
Телефон: {data["phone"]}

Вид вклада: {data["deposit_type"]}
Сумма вклада: {data["amount"]}
Процентная ставка: {data["interest_rate"]}%
Дата начала: {data["start_date"]}
Дата окончания: {data["end_date"]}
Срок вклада: {data["term_months"]} мес.

Капитализация: {"Да" if data["capitalization"] else "Нет"}
Автопролонгация: {"Да" if data["auto_renewal"] else "Нет"}

Особые условия:
{data["special_conditions"] or "Отсутствуют"}
'''.strip()

    return text
