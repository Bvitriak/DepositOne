from fastapi.responses import JSONResponse

from services import country_service


def list_countries(connection):
    result, status = country_service.list_countries(connection)
    return JSONResponse(result, status_code=status)
