import jwt
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from app.format_models import Token, TokenData
from app.db_models import User, Log
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.dependencies import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

TokenDep = Annotated[str, Depends(oauth2_scheme)]

router = APIRouter()

SECRET_KEY = "1a3706bbe01685b0c724b6581d3b08b655cbc2d732e2854e2874767dc1d85187"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(User).where(User.mobile == username)).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: TokenDep, session: Annotated[Session, Depends(get_session)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION
    user = session.exec(select(User).where(User.mobile == username and User.is_enabled)).first()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def add_log(session: Annotated[Session, Depends(get_session)],
                  current_user: Annotated[User, Depends(get_session)]):
    log = Log(user=current_user, date_time=datetime.now(), ip_address="")
    session.add(log)
    session.commit()


@router.post("/token", tags=["security"])
async def login_for_access_token(form_data: LoginFormDep, session: Annotated[Session, Depends(get_session)],
                                 background_tasks: BackgroundTasks) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.mobile}, expires_delta=access_token_expires
        )

        background_tasks.add_task(add_log, session=session, current_user=user)
        return Token(access_token=access_token, token_type="bearer")

# print(get_password_hash('admin'))
