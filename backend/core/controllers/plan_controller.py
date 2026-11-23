from fastapi.responses import JSONResponse

from services import plan_service
from utils import currency
from utils.params import read_list_params


def list_plans(connection, query_params):
    search, sort, order, page, page_size = read_list_params(query_params, "payout", "asc")
    result, status = plan_service.list_plans(connection, search, sort, order, page, page_size)
    return JSONResponse(result, status_code=status)


def get_summary(connection, query_params):
    result, status = plan_service.get_summary(connection, currency.normalize(query_params.get("currency")))
    return JSONResponse(result, status_code=status)


def get_plan(connection, deposit_id):
    result, status = plan_service.get_plan(connection, deposit_id)
    return JSONResponse(result, status_code=status)
