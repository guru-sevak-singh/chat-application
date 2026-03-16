# ROUTER RESPONSIBLE FOR THE USERS ONLY.
from fastapi import APIRouter, status, Depends, HTTPException
from models import Users

from sqlalchemy.orm import Session

from utils import db_dependency, get_current_user

from typing import Annotated

router = APIRouter(
    prefix='/users',
    tags=['users']
)

user_dependency = Annotated[Session, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def all_users(user: user_dependency,db : db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized Access')
    return db.query(Users).all()