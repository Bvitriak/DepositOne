def upcoming_payouts(connection, start_date, end_date):
    query = (
        "SELECT dep.first_name, dep.last_name, d.end_date "
        "FROM deposits d JOIN depositors dep ON dep.id = d.depositor_id "
        "WHERE d.status = 'Active' AND d.end_date BETWEEN %s AND %s "
        "ORDER BY d.end_date ASC"
    )
    with connection.cursor() as cursor:
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()


def pending_contracts(connection):
    query = (
        "SELECT dep.first_name, dep.last_name, ct.contract_date "
        "FROM contracts ct JOIN deposits d ON d.id = ct.deposit_id "
        "JOIN depositors dep ON dep.id = d.depositor_id "
        "WHERE ct.signing_status = 'Pending' ORDER BY ct.contract_date ASC"
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
