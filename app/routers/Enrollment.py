from typing import Annotated, List
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from starlette import status
from app.dependencies import get_session
from app.db_models import User, Presenting, Enrollment
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from app.format_models import EnrollmentPublic

router = APIRouter()

@router.get("/presenting/", tags=["presenting"], response_model= List[Presenting])
async def get_presenting_list (current_user: Annotated[User,Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    presenting =  session.exec(select(Presenting)).all()
    if presenting:
        return presenting
    raise HTTPException(status_code=404, detail="Presenting not found!")

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
async def get_all_enrollment(current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
        enrollment_name: str = Query(None, description="Search by last name (optional)"),
        limit: int = 50,
        offset: int = 0):

    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    query = select(Enrollment)
    if enrollment_name:
        query = query.where(Enrollment.name.like(f"%{enrollment_name}%"))
    query = query.offset(offset).limit(limit)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="Enrollment not found!")

    return result


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


