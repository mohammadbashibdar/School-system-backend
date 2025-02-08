from typing import Annotated, List, Optional
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, update, delete, or_
from app.dependencies import get_session
from app.db_models import Credit, User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from app.format_models import FilterParams

router = APIRouter()


# Add Credit
@router.post("/credits/add", tags=["credits"], response_model=Credit)
async def add_credit(credit: Credit,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        new_credit = Credit.model_validate(credit)
        session.add(new_credit)
        session.commit()
        session.refresh(new_credit)
        return new_credit
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while adding Credit: {e}")


# Read All Credits
@router.get("/credits/", tags=["credits"], response_model=List[Credit])
async def get_all_credits(

        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
        filter_query: Annotated[FilterParams, Query()]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Credit)

    if filter_query.query:
        query = query.where(or_(Credit.teacher_id.contains(filter_query.query),
                                Credit.amount.contains(filter_query.query)))  # Filter by teacher_id or amount

    if filter_query.order_by:
        try:
            sort_column = getattr(Credit, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)
    return session.exec(query).all()


# Read Credit by ID
@router.get("/credits/{credit_id}", tags=["credits"], response_model=Credit)
async def get_credit(credit_id: int,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    credit = session.get(Credit, credit_id)
    if credit:
        return credit
    raise HTTPException(status_code=404, detail="Credit not found!")


# Update Credit
@router.put("/credits/{credit_id}", tags=["credits"], response_model=Credit)
async def update_credit(credit_id: int, credit_data: Credit,
                        current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    existing_credit = session.get(Credit, credit_id)
    if existing_credit:
        for key, value in credit_data.model_dump(exclude_unset=True).items():
            setattr(existing_credit, key, value)
        session.add(existing_credit)
        session.commit()
        session.refresh(existing_credit)
        return existing_credit
    raise HTTPException(status_code=404, detail="Credit not found!")


# Delete Credit
@router.delete("/credits/{credit_id}", tags=["credits"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_credit(credit_id: int,
                        current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    existing_credit = session.get(Credit, credit_id)
    if existing_credit:
        session.delete(existing_credit)
        session.commit()
        return {"detail": "Credit deleted successfully!"}
    raise HTTPException(status_code=404, detail="Credit not found!")
