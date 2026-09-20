PAGE_SIZES = [10, 25, 50]


def paginate(total, page, page_size):
    if page_size not in PAGE_SIZES:
        page_size = PAGE_SIZES[0]
    pages = max(1, -(-total // page_size))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    offset = (page - 1) * page_size
    return page, pages, page_size, offset
