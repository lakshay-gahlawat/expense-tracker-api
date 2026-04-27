import math


def paginate(query, page: int, limit: int, sort_by, order, allowed_sort_fields, default_sort_column):
    page = max(1, page)
    limit = max(1, min(limit, 100))

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 0

    # clamp page to valid range
    if pages > 0:
        page = min(page, pages)

    offset = (page - 1) * limit

    # sorting
    order = (order or "asc").lower()
    if order not in ("asc", "desc"):
        order = "asc"

    if sort_by and sort_by in allowed_sort_fields:
        column = allowed_sort_fields[sort_by]
    else:
        column = default_sort_column

    if order == "desc":
        query = query.order_by(column.desc(), default_sort_column.asc())
    else:
        query = query.order_by(column.asc(), default_sort_column.asc())

    items = query.limit(limit).offset(offset).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
