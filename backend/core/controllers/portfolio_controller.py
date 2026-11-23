from fastapi.responses import JSONResponse

from services import portfolio_service
from utils import currency


def get_portfolio(connection, query_params):
    result, status = portfolio_service.get_portfolio(connection, currency.normalize(query_params.get("currency")))
    return JSONResponse(result, status_code=status)
