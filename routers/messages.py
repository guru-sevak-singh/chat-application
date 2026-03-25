from fastapi import APIRouter, Query, Depends
from models import Messages
from utils import db_dependency, get_db
from pydantic import BaseModel

from typing import TypeVar, Generic, List

T = TypeVar("T")

router = APIRouter(
    prefix='/messages',
    tags=['Messages']
)

class PaginationPerms(BaseModel):
    page : int = 1
    page_size : int = 10

class PageResponse(BaseModel, Generic[T]):
    total : int
    page : int
    page_size : int
    items : List[T]


# Pagination query
def pagination(query, page : int, page_size : int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get('/get-all-messages/{room_id}', response_class=PageResponse)
def get_all_messages(
    room_id : int, db : db_dependency, 
    page : int = Query(1, ge=1, description='Page Number'),
    page_size : int = Query(10, ge=10, le=100, description='Page Size')):
    messages = db.query(Messages).filter(Messages.room_id == room_id).all()
    return messages