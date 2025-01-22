from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from app.db_models import Teacher, User
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams

router = APIRouter()


@router.post("/teachers/add", tags=["teachers"], response_model=Teacher)
async def add_teacher(teacher1: Teacher,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]

                      ):
    """Add a new teacher."""
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_teacher = Teacher.model_validate(teacher1)
        session.add(temp_teacher)
        session.commit()
        session.refresh(temp_teacher)
        return temp_teacher
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding teacher: {e}")


@router.get("/teachers/", tags=["teachers"])
async def get_teachers(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    """Retrieve all teachers with pagination."""
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Teacher)

    if filter_query.query:
        query = query.where(or_(Teacher.name.contains(filter_query.query),
                                Teacher.email_address.contains(filter_query.query)))  # Filter by name (partial match)

    if filter_query.order_by:
        try:
            sort_column = getattr(Teacher, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)
    # # Call the paginate function
    # paginated_result = paginate(query=query, session=session, page=page, page_size=page_size)
    # if not paginate:
    #     raise HTTPException(status_code=404, detail=f"No {paginate} found")

    return session.exec(query).all()


@router.get("/teachers/{teacher_id}", tags=["teachers"], response_model=Teacher)
async def get_teacher(teacher_id: int,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    """Retrieve a teacher by ID."""
    teacher2 = session.get(Teacher, teacher_id)
    if not teacher2:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher2


@router.put("/teachers/{teacher_id}", tags=["teachers"], response_model=Teacher)
async def update_teacher(
        teacher_id: int, teacher_data: Teacher, current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    """Update a teacher's information."""
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    teacher3 = session.get(Teacher, teacher_id)
    if not teacher3:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for key, value in teacher_data.dict(exclude_unset=True).items():
        setattr(teacher3, key, value)
    session.add(teacher3)
    session.commit()
    session.refresh(teacher3)
    return teacher3


@router.delete("/teachers/{teacher_id}", tags=["teachers"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(teacher_id: int, current_user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[Session, Depends(get_session)]):
    """Delete a teacher by ID."""
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    session.delete(teacher)
    session.commit()
    return {"detail": "Teacher deleted successfully"}
