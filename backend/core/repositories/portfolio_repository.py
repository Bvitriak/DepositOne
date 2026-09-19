from models.portfolio import Portfolio
from utils import currency

ACTIVE_STATUS = "Active"
SIGNED_STATUS = "Signed"
PENDING_STATUS = "Pending"
REJECTED_STATUS = "Rejected"

QUERY = (
    "SELECT "
    "(SELECT count(*) FROM depositors), "
    "(SELECT count(*) FROM deposits WHERE status = %s), "
    "(SELECT COALESCE(sum(" + currency.in_rubles("d.amount", "c.code") + "), 0) FROM deposits d JOIN currencies c ON c.id = d.currency_id WHERE d.status = 'Active'), "
    "(SELECT count(*) FROM contracts WHERE signing_status = %s), "
    "(SELECT count(*) FROM contracts WHERE signing_status = %s), "
    "(SELECT count(*) FROM contracts WHERE signing_status = %s)"
)


def get_portfolio(connection):
    parameters = (ACTIVE_STATUS, SIGNED_STATUS, PENDING_STATUS, REJECTED_STATUS)
    with connection.cursor() as cursor:
        cursor.execute(QUERY, parameters)
        row = cursor.fetchone()
    return Portfolio(
        depositors=row[0],
        active_deposits=row[1],
        total_amount=row[2],
        signed_contracts=row[3],
        pending_contracts=row[4],
        rejected_contracts=row[5],
    )
