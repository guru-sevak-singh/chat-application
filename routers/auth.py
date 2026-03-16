from fastapi import APIRouter, status, HTTPException, Depends
from utils import db_dependency, hash_password, TokenData, create_access_token, verify_password
from models import Users

from pydantic import BaseModel

from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
##########################################################################################################################
################################################## APIS / ROUTERS ########################################################
##########################################################################################################################
# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

class RegisterUser(BaseModel):
    name : str
    phone_number : str
    password : str

# output for the login
class Token(BaseModel):
    access_token : str
    token_type : str
    user_id : int

class LoginSchema(BaseModel):
    username: str
    password : str

# ──────────────  REGISTER ───────────────────────────────────────────────────────────────────────────────────────────────
@router.post("/register", status_code=status.HTTP_201_CREATED)
def regiester_user(db: db_dependency, payload : RegisterUser):
    '''
    This function will first check whether the user was existing or not
    and if not exist then it will create a new User
    '''
    payload = payload.model_dump()
    existing = db.query(Users).filter(Users.phone_number == payload.get("phone_number")).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User Already Exists')
    
    payload['hashed_password'] = hash_password(payload.get("password"))

    del payload['password']

    obj = Users(**payload)
    db.add(obj)
    db.commit()

    del payload['hashed_password']

    payload.update({"message": "User Created Successfully"})
    return payload


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(
    # form_data : Annotated[OAuth2PasswordRequestForm, Depends()],
    form_data : LoginSchema,
    db : db_dependency) -> Token:

    user = db.query(Users).filter(Users.phone_number == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Username or Password')

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Username or Password')

    user_data = {
        "sub":user.phone_number,
        "id": user.id
        }

    access_token = create_access_token(user_data)

    return Token(access_token=access_token, token_type="bearer", user_id=user_data.get("id"))
