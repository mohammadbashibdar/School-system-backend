from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session
from sqlmodel import Session, select
import app.db_models
from app.dependencies import get_session
from app.format_models import UserInDB, UserPublic
from app.db_models import Building,Room,Schedule
from app.db_models import User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION, get_password_hash
from typing import List
# from flask import Flask

router = APIRouter()


@router.get("/buildings/", tags=["buildings"], response_model=List[Building])
async def get_buildings( current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    building_read=session.exec(select(Building)).all()
    if not building_read:
        raise HTTPException(status_code=404, detail=f"Building not found")
    return building_read

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

@router.get("/schedules/", tags=["schedules"], response_model=List[Schedule])
async def get_schedules( current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read=session.exec(select(Schedule)).all()
    if not schedule_read:
        raise HTTPException(status_code=404, detail=f"Schedule not found")
    return schedule_read

@router.get("/schedules/{schedules_id}", tags=["schedules"], response_model=Schedule)
async def read_schedule_me(schedule_id:int, current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    schedule_read = session.get(Schedule, schedule_id)
    if not schedule_read:
        raise HTTPException(status_code=404, detail=f"Schedule not found")
    return schedule_read

@router.put("/schedules/{schedule_name}", tags=["schedules"], response_model=Schedule)
async def update_schedule(schedule_id: int, schedule_data: Schedule, current_user: Annotated[User, Depends(get_current_user)],
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