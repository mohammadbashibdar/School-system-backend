from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from app.dependencies import get_session
from app.format_models import UserPublic, FilterParams
from app.db_models import User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()


@router.post("/users/add", tags=["users"], response_model=User)
async def add_user(user: UserPublic, session: Annotated[User, Depends(get_current_user)],
                   current_user: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_user = User.model_validate(user)
        existing_user = session.exec(select(User).where(User.mobile == user.mobile)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        if not existing_user:
            session.add(temp_user)
            session.commit()
            session.refresh(temp_user)
            return temp_user

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An Error occurred during adding User: {e}")


@router.get("/users/me", tags=["users"], response_model=UserPublic)
async def read_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/users/{username}", tags=["users"], response_model=UserPublic)
async def get_user(username: str, current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    query_user = session.exec(select(User).where(User.mobile == username)).first()
    if query_user:
        return query_user
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/users/", tags=["users"])
async def get_all_users(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    # Define the base query
    query = select(User)
    if filter_query.query:
        query = query.where(or_(User.name.contains(filter_query.query),
                                User.email_address.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(User, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)
    return session.exec(query).all()


@router.put("/users/update/{user_id}", tags=["users"], response_model=UserPublic)
async def update_user(user_id: int, user_data: User, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    update_users = session.get(User, user_id)
    if update_users:
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(update_users, key, value)
        session.add(update_users)
        session.commit()
        session.refresh(update_users)
        return update_users
    raise HTTPException(status_code=404, detail="users not found!")


@router.delete("/users/delete/{user_id}", tags=["users"])
async def delete_user(user_id: int, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    delete_users = session.get(User, user_id)
    if delete_users:
        session.delete(delete_users)
        session.commit()
        return {"detail": "user deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found!")
