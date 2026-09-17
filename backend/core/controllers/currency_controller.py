from fastapi.responses import JSONResponse

from services import currency_service


def list_currencies(connection):
    result, status = currency_service.list_currencies(connection)
    return JSONResponse(result, status_code=status)
