from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import session
from sqlmodel import Session, select
from app.dependencies import get_session
from app.db_models import Building, Room, Schedule
from app.db_models import User
from app.format_models import FilterParams
from sqlalchemy import or_
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION, get_password_hash
from typing import List

router = APIRouter()

@router.post("/schedules/add", tags=["schedules"], response_model=Schedule)
async def add_schedule(schedule_add: Schedule, current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_schedule = schedule_add.model_validate(schedule_add)
        session.add(temp_schedule)
        session.commit()
        session.refresh(temp_schedule)
        return temp_schedule
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error Adding Schedule")


# ? filter params
@router.get("/schedules/", tags=["schedules"], response_model=List[Schedule])
async def get_schedules(current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)],
                         filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read = session.exec(select(Schedule)).all()
    if filter_query.query:
        query= schedule_read.where(or_(Schedule.schedule_id.contains(filter_query.query),
                                       Schedule.student_id.contains(filter_query.query)))
    if filter_query.order_by:
        try:
            sort:getattr(Schedule, filter_query.order_by)
            query = query.order_by(sort.asc() if filter_query.order_type == "asc" else sort.desc())
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"rollcall not found")
    if not schedule_read:
        raise HTTPException(status_code=404, detail=f"Schedule not found")
    return schedule_read


@router.get("/schedules/{schedules_id}", tags=["schedules"], response_model=Schedule)
async def read_schedule_me(schedule_id: int, current_user: Annotated[User, Depends(get_current_user)],
                           session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read = session.get(Schedule, schedule_id)
    if not schedule_read:
        raise HTTPException(status_code=404, detail=f"Schedule not found")
    return schedule_read


@router.put("/schedules/{schedule_name}", tags=["schedules"], response_model=Schedule)
async def update_schedule(schedule_id: int, schedule_data: Schedule,
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read = session.get(Schedule, schedule_id)
    if not schedule_read:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for key, value in schedule_data.dict(exclude_unset=True).items():
        setattr(schedule_read, key, value)
    session.add(schedule_read)
    session.commit()
    session.refresh(schedule_read)
    return schedule_read


@router.delete("/schedules/{schedule_id}", tags=["schedules"], response_model=Schedule)
async def delete_schedule(schedule_id: int, current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read = session.get(Schedule, schedule_id)
    if not schedule_read:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session.delete(schedule_read)
    session.commit()
    session.refresh(schedule_read)
    return {"message": f"Schedule {schedule_id} deleted"}
