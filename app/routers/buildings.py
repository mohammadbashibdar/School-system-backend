from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import session
from sqlmodel import Session, select
from app.format_models import FilterParams
from sqlalchemy import or_
from app.dependencies import get_session
from app.db_models import Building
from app.db_models import User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION, get_password_hash
from typing import List

router = APIRouter()


# Error handling...
@router.post("/buildings/add", tags=["buildings"], response_model=Building)
async def add_building(building_add: Building, current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_building = building_add.model_validate(building_add)
        session.add(temp_building)
        session.commit()
        session.refresh(temp_building)
        return temp_building
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Adding Building\n{str(e)}")


# ? filter params ..................
@router.get("/buildings/", tags=["buildings"], response_model=List[Building])
async def get_buildings(current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)],
                         filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    building_read = session.exec(select(Building)).all()
    if filter_query.query:
        query= building_read.where(or_(Building.schedule_id.contains(filter_query.query),
                                       Building.student_id.contains(filter_query.query)))
    if filter_query.order_by:
        try:
            sort:getattr(Building, filter_query.order_by)
            query = query.order_by(sort.asc() if filter_query.order_type == "asc" else sort.desc())
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"Building not found")
    if not building_read:
        raise HTTPException(status_code=404, detail=f"rollcall not found")
    return building_read
    # return [{"building_name": "sama"}, {"num_floors": "1"}, {"num_rooms": "101"}, {"capacity": "10"}]

@router.get("/buildings/{buildings_id}", tags=["buildings"], response_model=Building)
async def read_building_me(building_id: int, current_user: Annotated[User, Depends(get_current_user)],
                           session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    building_read = session.get(Building, building_id)
    if not building_read:
        raise HTTPException(status_code=404, detail=f"Building not found")
    return building_read


@router.put("/buildings/{building_name}", tags=["buildings"], response_model=Building)
async def update_building(building_id: int, building_data: Building,
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    building_read = session.get(Building, building_id)
    if not building_read:
        raise HTTPException(status_code=404, detail="Building not found")
    for key, value in building_data.dict(exclude_unset=True).items():
        setattr(building_read, key, value)
    session.add(building_read)
    session.commit()
    session.refresh(building_read)
    return building_read


@router.delete("/buildings/{building_id}", tags=["buildings"], response_model=Building)
async def delete_building(building_id: int, current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    building_read = session.get(Building, building_id)
    if not building_read:
        raise HTTPException(status_code=404, detail="Building not found")
    session.delete(building_read)
    session.commit()
    session.refresh(building_read)
    return {"message": f"Building {building_id} deleted"}
