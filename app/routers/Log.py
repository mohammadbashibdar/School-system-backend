from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, Query
from sqlmodel import Session, select, or_
from app.dependencies import get_session
from app.format_models import Log, FilterParams
from app.db_models import User, Log
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe

router = APIRouter()


# @router.post("/login", tags=["logs"])
# async def add_log(username, password: str, session: Annotated[Session, Depends(get_session)],
#                   current_user: Annotated[User, Depends(get_session)]):
#     user_added = Session.exec(select(Log).filter(Log.username == username)).first()
#     if not current_user or (user_added and user_added.hashed_password != password):
#         raise HTTPException(status_code=404, detail="Invalid credentials")
#
#     log = Log(user_id=current_user.id, username=current_user.name, timestamp=datetime.now())
#     session.add(log)
#     session.commit()
#
#     return {"massage": "Login successful"}
#

@router.get("/log/read/{log_id}", tags=["logs"])
async def read_log(session: Annotated[Session, Depends(get_session)]):
    logs = session.exec(select(Log)).all()
    if not logs:
        raise HTTPException(status_code=404, detail="no logs found")
    return logs


@router.delete("/log/delete/{log_id}", tags=["logs"])
async def delete_log(log_id: Log.id, session: Annotated[Session, Depends(get_session)]):
    delete_logs = session.get(Log, log_id)
    if delete_logs:
        session.delete(delete_logs)
        session.commit()
        session.refresh(delete_logs)
        return {"details": "log deleted successfully"}
    raise HTTPException(status_code=404, detail=" log not found")


@router.get("/get/login", tags=["logs"])
async def get_logins(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Log)

    if filter_query.query:
        query = query.where(or_(Log.username.contains(filter_query.query),
                                Log.id.contains(filter_query.query)))  # Filter by name (partial match)

    if filter_query.order_by:
        try:
            sort_column = getattr(Log, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()
