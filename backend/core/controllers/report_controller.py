from fastapi.responses import JSONResponse

from services import report_service
from utils import currency


def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def list_reports(connection, query_params):
    search = (query_params.get("search") or "").strip()
    sort = query_params.get("sort") or "amount"
    order = query_params.get("order") or "desc"
    page = to_int(query_params.get("page"), 1)
    page_size = to_int(query_params.get("page_size"), 10)
    code = currency.normalize(query_params.get("currency"))
    result, status = report_service.list_reports(connection, search, sort, order, page, page_size, code)
    return JSONResponse(result, status_code=status)


def get_cash_flow(connection, query_params):
    result, status = report_service.get_cash_flow(connection, currency.normalize(query_params.get("currency")))
    return JSONResponse(result, status_code=status)
