from math import ceil

def normalize_page(page, default: int = 1) -> int:
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = default
    return max(page, 1)

def normalize_page_size(page_size, default: int = 20, max_size: int = 100) -> int:
    try:
        page_size = int(page_size)
    except (TypeError, ValueError):
        page_size = default
    return max(1, min(page_size, max_size))

def build_pagination_meta(total: int, page: int, page_size: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
        "has_prev": page > 1,
        "has_next": page * page_size < total,
    }
