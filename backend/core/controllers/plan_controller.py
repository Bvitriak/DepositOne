from fastapi.responses import JSONResponse

from services import plan_service


def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def list_plans(connection, query_params):
    search = (query_params.get("search") or "").strip()
    sort = query_params.get("sort") or "payout"
    order = query_params.get("order") or "asc"
    page = to_int(query_params.get("page"), 1)
    page_size = to_int(query_params.get("page_size"), 10)
    result, status = plan_service.list_plans(connection, search, sort, order, page, page_size)
    return JSONResponse(result, status_code=status)


def get_summary(connection):
    result, status = plan_service.get_summary(connection)
    return JSONResponse(result, status_code=status)


def get_plan(connection, deposit_id):
    result, status = plan_service.get_plan(connection, deposit_id)
    return JSONResponse(result, status_code=status)
