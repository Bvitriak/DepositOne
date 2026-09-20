def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def read_list_params(query_params, default_sort, default_order):
    search = (query_params.get("search") or "").strip()
    sort = query_params.get("sort") or default_sort
    order = query_params.get("order") or default_order
    page = to_int(query_params.get("page"), 1)
    page_size = to_int(query_params.get("page_size"), 10)
    return search, sort, order, page, page_size
