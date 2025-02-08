from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlmodel import Session, select, update, delete, or_

from app.db_models import Payment, User
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams

router = APIRouter()


@router.post("/payments/add", tags=["payments"], response_model=Payment)
async def add_payment(payment1: Payment,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]

                      ):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_lesson = Payment.model_validate(payment1)
        session.add(temp_lesson)
        session.commit()
        session.refresh(temp_lesson)
        return temp_lesson
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while adding Payment: {e}")


@router.get("/payments/", tags=["payments"])
async def get_payments(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Payment)

    if filter_query.query:
        query = query.where(or_(Payment.id.contains(filter_query.query), Payment.user_id.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(Payment, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/payments/{payment_id}", tags=["payments"], response_model=Payment)
async def get_payment(payment_id: int,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    payment2 = session.get(Payment, payment_id)
    if not payment2:
        raise HTTPException(status_code=404, detail="payment not found.")
    return payment2


@router.put("/payments/{payment_id}", tags=["payments"], response_model=Payment)
async def update_payment(
        payment_id: int, payment_data: Payment, current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    payment3 = session.get(Payment, payment_id)
    if not payment3:
        raise HTTPException(status_code=404, detail="Payment not found.")
    for key, value in payment_data.dict(exclude_unset=True).items():
        setattr(payment3, key, value)
    session.add(payment3)
    session.commit()
    session.refresh(payment3)
    return payment3

# where is delete endpoint ?
