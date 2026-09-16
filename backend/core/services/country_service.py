from repositories import country_repository


def list_countries(connection):
    return {"countries": country_repository.list_countries(connection)}, 200
