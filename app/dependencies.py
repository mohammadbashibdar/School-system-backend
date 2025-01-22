# from typing import Annotated
from .db_models import engine, User
# from fastapi import Depends
from sqlmodel import Session

# async def get_token_header(x_token: Annotated[str, Header()]):
#     if x_token != "fake-super-secret-token":
#         raise HTTPException(status_code=400, detail="X-Token header invalid")
#
#
# async def get_query_token(token: str):
#     if token != "jessica":
#         raise HTTPException(status_code=400, detail="No Jessica token provided")


def get_session():
    with Session(engine) as session:
        yield session

