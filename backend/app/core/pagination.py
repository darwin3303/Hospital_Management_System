from fastapi import Query
from pydantic import BaseModel


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


def page_params(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def paginate_meta(page: int, page_size: int, total: int) -> dict:
    return {"page": page, "page_size": page_size, "total": total}
