from math import ceil
from typing import Any, Mapping, Sequence
from core_service.app.db import get_db

def _normalize_page(page: Any) -> int:
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    return max(page, 1)

def _normalize_page_size(
    page_size: Any,
    default: int = 20,
    max_size: int = 100,
) -> int:
    try:
        page_size = int(page_size)
    except (TypeError, ValueError):
        page_size = default
    return max(1, min(page_size, max_size))

def _build_paginated_result(
    items: Sequence[Mapping[str, Any]],
    total: int,
    page: int,
    page_size: int,
    filters: Mapping[str, Any],
    sorting: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "has_prev": page > 1,
            "has_next": page * page_size < total,
        },
        "filters": dict(filters),
        "sorting": dict(sorting),
    }

def search_depositors(
    search: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int | str = 1,
    page_size: int | str = 20,
) -> dict[str, Any]:
    db = get_db()

    allowed_sort_fields: dict[str, str] = {
        "id": "d.id",
        "lastname": "d.lastname",
        "firstname": "d.firstname",
        "email": "d.email",
        "phone": "d.phone",
        "created_at": "d.createdat",
    }

    sort_column = allowed_sort_fields.get(sort_by, "d.id")
    direction = "ASC" if str(sort_order).lower() == "asc" else "DESC"
    page_int = _normalize_page(page)
    page_size_int = _normalize_page_size(page_size)
    offset = (page_int - 1) * page_size_int

    where: list[str] = []
    params: list[Any] = []

    if search and search.strip():
        term = f"%{search.strip()}%"
        where.append("""
            (
                lower(d.lastname) LIKE lower(?) OR
                lower(d.firstname) LIKE lower(?) OR
                lower(coalesce(d.middlename, '')) LIKE lower(?) OR
                d.passportseries LIKE ? OR
                d.passportnumber LIKE ? OR
                lower(coalesce(d.address, '')) LIKE lower(?)
            )
        """)
        params.extend([term, term, term, term, term, term])

    if phone and phone.strip():
        where.append("coalesce(d.phone, '') LIKE ?")
        params.append(f"%{phone.strip()}%")

    if email and email.strip():
        where.append("lower(coalesce(d.email, '')) LIKE lower(?)")
        params.append(f"%{email.strip()}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM depositors d
        {where_sql}
    """

    data_sql = f"""
        SELECT
            d.id,
            d.lastname,
            d.firstname,
            d.middlename,
            d.passportseries AS passport_series,
            d.passportnumber AS passport_number,
            d.phone,
            d.email,
            d.address,
            d.createdat AS created_at
        FROM depositors d
        {where_sql}
        ORDER BY {sort_column} {direction}, d.id DESC
        LIMIT ? OFFSET ?
    """

    total = db.execute(count_sql, params).fetchone()["total"]
    rows = db.execute(data_sql, [*params, page_size_int, offset]).fetchall()

    return _build_paginated_result(
        items=rows,
        total=total,
        page=page_int,
        page_size=page_size_int,
        filters={
            "search": search or "",
            "phone": phone or "",
            "email": email or "",
        },
        sorting={
            "sort_by": sort_by,
            "sort_order": direction.lower(),
        },
    )

def search_deposits(
    search: str | None = None,
    status: str | None = None,
    currency: str | None = None,
    min_amount: float | str | None = None,
    max_amount: float | str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int | str = 1,
    page_size: int | str = 20,
) -> dict[str, Any]:
    db = get_db()

    allowed_sort_fields = {
        "id": "d.id",
        "amount": "d.amount",
        "interest_rate": "d.interest_rate",
        "start_date": "d.start_date",
        "end_date": "d.end_date",
        "status": "d.status",
        "deposit_type": "d.deposit_type",
        "last_name": "dep.lastname",
    }

    sort_column = allowed_sort_fields.get(sort_by, "d.id")
    direction = "ASC" if str(sort_order).lower() == "asc" else "DESC"
    page_int = _normalize_page(page)
    page_size_int = _normalize_page_size(page_size)
    offset = (page_int - 1) * page_size_int

    where = []
    params = []

    if search:
        term = f"%{search.strip()}%"
        where.append("""
            (
                lower(dep.lastname) LIKE lower(?) OR
                lower(dep.firstname) LIKE lower(?) OR
                lower(coalesce(dep.middlename, '')) LIKE lower(?) OR
                lower(d.deposit_type) LIKE lower(?)
            )
        """)
        params.extend([term, term, term, term])

    if status:
        where.append("d.status = ?")
        params.append(status)

    if currency:
        where.append("d.currency = ?")
        params.append(currency)

    if min_amount not in (None, ""):
        where.append("CAST(d.amount AS REAL) >= ?")
        params.append(min_amount)

    if max_amount not in (None, ""):
        where.append("CAST(d.amount AS REAL) <= ?")
        params.append(max_amount)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM deposits d
        JOIN depositors dep ON dep.id = d.depositor_id
        {where_sql}
    """

    data_sql = f"""
        SELECT
            d.id,
            d.depositor_id,
            d.deposit_type,
            d.amount,
            d.interest_rate,
            d.start_date,
            d.end_date,
            d.status,
            d.currency,
            d.capitalization,
            d.auto_renewal,
            dep.lastname,
            dep.firstname,
            dep.middlename
        FROM deposits d
        JOIN depositors dep ON dep.id = d.depositor_id
        {where_sql}
        ORDER BY {sort_column} {direction}, d.id DESC
        LIMIT ? OFFSET ?
    """

    total = db.execute(count_sql, params).fetchone()["total"]
    rows = db.execute(data_sql, [*params, page_size_int, offset]).fetchall()

    return _build_paginated_result(
        items=rows,
        total=total,
        page=page_int,
        page_size=page_size_int,
        filters={
            "search": search or "",
            "status": status or "",
            "currency": currency or "",
            "min_amount": min_amount if min_amount is not None else "",
            "max_amount": max_amount if max_amount is not None else "",
        },
        sorting={
            "sort_by": sort_by,
            "sort_order": direction.lower(),
        },
    )

def search_contracts(
    search: str | None = None,
    is_signed: int | str | None = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    page: int | str = 1,
    page_size: int | str = 20,
) -> dict[str, Any]:
    db = get_db()

    allowed_sort_fields: dict[str, str] = {
        "id": "c.id",
        "contract_number": "c.contract_number",
        "contract_date": "c.contract_date",
        "deposit_id": "c.deposit_id",
        "last_name": "dep.lastname",
    }

    sort_column = allowed_sort_fields.get(sort_by, "c.id")
    direction = "ASC" if str(sort_order).lower() == "asc" else "DESC"
    page_int = _normalize_page(page)
    page_size_int = _normalize_page_size(page_size)
    offset = (page_int - 1) * page_size_int

    where: list[str] = []
    params: list[Any] = []

    if search and search.strip():
        term = f"%{search.strip()}%"
        where.append(
            """
            (
                lower(c.contract_number) LIKE lower(?)
                OR lower(dep.lastname) LIKE lower(?)
                OR lower(dep.firstname) LIKE lower(?)
                OR CAST(c.deposit_id AS TEXT) LIKE ?
            )
            """
        )
        params.extend([term, term, term, term])

    if is_signed in (0, 1, "0", "1"):
        where.append("c.is_signed = ?")
        params.append(int(is_signed))

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM contracts c
        JOIN deposits d ON d.id = c.deposit_id
        JOIN depositors dep ON dep.id = d.depositor_id
        {where_sql}
    """

    data_sql = f"""
        SELECT
            c.id,
            c.contract_number,
            c.contract_date,
            c.deposit_id,
            c.is_signed,
            dep.lastname,
            dep.firstname,
            dep.middlename
        FROM contracts c
        JOIN deposits d ON d.id = c.deposit_id
        JOIN depositors dep ON dep.id = d.depositor_id
        {where_sql}
        ORDER BY {sort_column} {direction}, c.id DESC
        LIMIT ? OFFSET ?
    """

    total = db.execute(count_sql, params).fetchone()["total"]
    rows = db.execute(data_sql, [*params, page_size_int, offset]).fetchall()

    return _build_paginated_result(
        items=rows,
        total=total,
        page=page_int,
        page_size=page_size_int,
        filters={
            "search": search or "",
            "is_signed": "" if is_signed is None else str(is_signed),
        },
        sorting={
            "sort_by": sort_by,
            "sort_order": direction.lower(),
        },
    )
