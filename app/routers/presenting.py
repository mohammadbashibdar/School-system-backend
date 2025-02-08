from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, update, delete, or_
from app.db_models import Presenting, User, Enrollment, Student, Course
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams

router = APIRouter()


@router.post("/presenting/add", tags=["presenting"], response_model=Presenting)
async def add_presenting(presenting_data: Presenting,
                         current_user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_presenting = Presenting.model_validate(presenting_data)
        session.add(temp_presenting)
        session.commit()
        session.refresh(temp_presenting)
        return temp_presenting
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding presenting: {e}")


@router.get("/presenting/", tags=["presenting"], response_model=List[Presenting])
async def get_presentings(
        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Presenting)

    if filter_query.query:
        query = query.where(
            or_(Presenting.term.contains(filter_query.query))
        )

    if filter_query.order_by:
        try:
            sort_column = getattr(Presenting, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)
    return session.exec(query).all()


@router.get("/presenting/{presenting_id}", tags=["presenting"], response_model=Presenting)
async def get_presenting(presenting_id: int,
                         current_user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    presenting = session.get(Presenting, presenting_id)
    if not presenting:
        raise HTTPException(status_code=404, detail="Presenting not found")
    return presenting




@router.put("/presenting/{presenting_id}", tags=["presenting"], response_model=Presenting)
async def update_presenting(presenting_id: int, presenting_data: Presenting,
                            current_user: Annotated[User, Depends(get_current_user)],
                            session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    presenting = session.get(Presenting, presenting_id)
    if not presenting:
        raise HTTPException(status_code=404, detail="Presenting not found")

    for key, value in presenting_data.dict(exclude_unset=True).items():
        setattr(presenting, key, value)

    session.add(presenting)
    session.commit()
    session.refresh(presenting)
    return presenting


@router.delete("/presenting/{presenting_id}", tags=["presenting"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_presenting(presenting_id: int,
                            current_user: Annotated[User, Depends(get_current_user)],
                            session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    presenting = session.get(Presenting, presenting_id)
    if not presenting:
        raise HTTPException(status_code=404, detail="Presenting not found")

    session.delete(presenting)
    session.commit()
    return {"detail": "Presenting deleted successfully"}
