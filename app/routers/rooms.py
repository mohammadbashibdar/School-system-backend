from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session
from sqlmodel import Session, select
import app.db_models
from app.dependencies import get_session
from app.format_models import UserInDB, UserPublic
from app.db_models import Building, Room
from app.db_models import User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION, get_password_hash
from typing import List

# from flask import Flask

router = APIRouter()


@router.get("/rooms/", tags=["rooms"], response_model=List[Room])
async def get_rooms(current_user: Annotated[User, Depends(get_current_user)],
                    session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    room_read = session.exec(select(Room)).all()
    if not room_read:
        raise HTTPException(status_code=404, detail=f"room not found")
    return room_read


@router.post("/rooms/add", tags=["rooms"], response_model=Room)
async def add_room(room_add: Room, current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    temp_room = room_add.model_validate(room_add)
    session.add(temp_room)
    session.commit()
    session.refresh(temp_room)

    # raise HTTPException(status_code=404, detail=f"Error Adding Room")
    return temp_room


@router.get("/rooms/", tags=["rooms"], response_model=List[Room])
async def get_rooms(current_user: Annotated[User, Depends(get_current_user)],
                    session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    room_read = session.exec(select(Room)).all()
    if not room_read:
        raise HTTPException(status_code=404, detail=f"Room not found")
    return room_read


@router.get("/rooms/{rooms_id}", tags=["rooms"], response_model=Room)
async def read_room_me(room_id: int, current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    room_read = session.get(Room, room_id)
    if not room_read:
        raise HTTPException(status_code=404, detail=f"Room not found")
    return room_read


@router.put("/rooms/{room_name}", tags=["rooms"], response_model=Room)
async def update_room(room_id: int, room_data: Room, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    room_read = session.get(Room, room_id)
    if not room_read:
        raise HTTPException(status_code=404, detail="Room not found")
    for key, value in room_data.dict(exclude_unset=True).items():
        setattr(room_read, key, value)
    session.add(room_read)
    session.commit()
    session.refresh(room_read)
    return room_read


@router.delete("/rooms/{room_id}", tags=["rooms"], response_model=Room)
async def delete_room(room_id: int, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    room_read = session.get(Room, room_id)
    if not room_read:
        raise HTTPException(status_code=404, detail="Room not found")
    session.delete(room_read)
    session.commit()
    session.refresh(room_read)
    return {"message": f"Room {room_id} deleted"}