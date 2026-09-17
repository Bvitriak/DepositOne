from repositories import currency_repository


def list_currencies(connection):
    return {"currencies": currency_repository.list_currencies(connection)}, 200
