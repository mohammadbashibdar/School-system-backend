from typing import Annotated, List
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from starlette import status
from app.dependencies import get_session
from app.db_models import User, Enrollment
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from app.format_models import EnrollmentPublic, FilterParams

router = APIRouter()

@router.post("/enrollment/", tags=["Enrollment"], response_model= List[Enrollment])
async def add_enrollment (enrollment: EnrollmentPublic,
                          current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permission:
                raise CREDENTIALS_EXCEPTION
        new_enrollment = Enrollment.model_validate(enrollment)
        session.add(new_enrollment)
        session.commit()
        session.refresh(new_enrollment)
        return new_enrollment
    except Exception as e:
        raise  HTTPException(status_code=400, detail= f"An Error occurred during adding Enrollment: {e}")

#Get all Enrollment

@router.get("/enrollment/", tags=["Enrollment"], response_model=List[Enrollment])
async def get_all_enrollments(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
        query_filter: Annotated[FilterParams, Query()]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Enrollment)
    if query_filter.query:
        query = query.where(or_(Enrollment.name.contains(query_filter.query),
                                Enrollment.id.contains(query_filter.query)))  # Filter by name (partial match)

    if query_filter.order_by:
        try:
            sort_column = getattr(Enrollment, query_filter.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if query_filter.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {query_filter.order_by}")

    query = query.offset((query_filter.page_number - 1) * query_filter.page_size).limit(query_filter.page_size)
    return session.exec(query).all()


#Read Enrollment by ID
@router.get("/enrollment/{enrollment_id}", tags = ["Enrollment"], response_model=Enrollment)
async def get_enrollment(enrollment_id: int,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        enrollment_self = session.get(Enrollment, enrollment_id)
        if enrollment_self:
            return enrollment_self
        raise HTTPException(status_code=404, detail="Enrollment not found!")

#Update Enrollment
@router.put("/enrollment/{enrollment_id}", tags = ["Enrollment"], response_model=Enrollment)
async def update_enrollment (enrollment_id: int, enrollment_data: Enrollment,
                          current_user: Annotated[User,Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    updated_enrollment = session.get(Enrollment, enrollment_id)
    if updated_enrollment:
        for key, value in enrollment_data.model_dump(exclude_unset=True).items():
            setattr(updated_enrollment, key, value)
        session.add(updated_enrollment)
        session.commit()
        session.refresh(updated_enrollment)
        return updated_enrollment
    raise HTTPException(status_code = 404, detail = "Enrollment not found!")

#Delete Enrollment
@router.delete("/enrollment/{enrollment_id}", tags = ["Enrollment"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(enrollment_id: int, current_user: Annotated[User,Depends(get_current_user)],
                            session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    deleted_enrollment = session.get(Enrollment, enrollment_id)
    if deleted_enrollment:
        session.delete(deleted_enrollment)
        session.commit()
        return {"detail": "enrollment deleted successfully!"}
    raise HTTPException(status_code = 404, detail = "Enrollment not found!")


