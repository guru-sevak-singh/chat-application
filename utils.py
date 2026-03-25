from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import status, Depends, HTTPException

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# from passlib.context import CryptContext
import bcrypt
from pydantic import BaseModel

from database import os, SessionalMaker




# ── CONFIG ──────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")    # use openssh rand -hex 32
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")
REFERESH_TOKEN_EXPIRES_MINUTES = os.getenv('REFERESH_TOKEN_EXPIRE_MINUTES')

# ── Hashing & Bearer ──────────────────────────────────────
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Pydantic Schemas ──────────────────────────────────────

class TokenData(BaseModel):
    phone_number : Optional[str] = None
    id : Optional[int] = None

class UserOut(BaseModel):
    id : int
    phone_number : str

# ── Password Helpers ──────────────────────────────────────
def hash_password(password : str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # return pwd_context.hash(password)

def verify_password(plain: str, hashed : str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())      # work with latest bcrypt version no need of pwd_context
    # return pwd_context.verify(plain, hashed)      # For the old version.

# ── JWT Helper ──────────────────────────────────────
def create_access_token(data : dict, expire_delta : Optional[timedelta] = 30) -> str:
    to_encode = data.copy()
    minutes = expire_delta if expire_delta else int(ACCESS_TOKEN_EXPIRES_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token : str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorised Access",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number : str = payload.get("sub")
        id : int = payload.get("id")

        if phone_number is None:
            raise credentials_exception
        return TokenData(phone_number=phone_number, id=id)
    
    except JWTError:
        raise credentials_exception


# ── FastAPI Dependency ──────────────────────────────────────
def get_current_user(token : Annotated[str, Depends(oauth2_schema)]) -> TokenData:
    'Injust this where we need current user form the application.'
    return decode_token(token=token)


async def get_db():
    db = SessionalMaker()
    try:
        yield db
    finally:
        db.close()

    
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]