from typing import Annotated, List
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlmodel import Session, select
from starlette import status
from app.dependencies import get_session
from app.db_models import Student, User
from app.format_models import StudentPublic
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()

#Add student
@router.post("/students/add",tags=["students"], response_model=Student)
async def add_student (student: StudentPublic,
                       current_user: Annotated[User,Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        new_student = Student.model_validate(student)
        session.add(new_student)
        session.commit()
        session.refresh(new_student)
        return new_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An Error occurred during adding Student:{e}")


@router.get("/students/", tags=["students"], response_model=List[Student])
async def get_all_students(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)],
        student_last_name: str = Query(None, descriptionli="Search by last name (optional)"),
        limit: int = 50,
        offset: int = 0,
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Student)
    if student_last_name:
        query = query.where(Student.name.like(f"%{student_last_name}%"))
    query = query.offset(offset).limit(limit)
    result = session.exec(query).all()
    if not result:
        raise HTTPException(status_code=404, detail="Students not found!")

    return result


#Read Student by ID
@router.get("/students/{student_id}", tags = ["students"], response_model=Student)
async def get_student(student_id: int,
                           current_user: Annotated[User, Depends(get_current_user)],
                           session: Annotated[Session, Depends(get_session)]):
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        student_self = session.get(Student,student_id)
        if student_self:
            return student_self
        raise HTTPException(status_code=404, detail="Student not found!")


#Update Student
@router.put("/students/{student_id", tags = ["students"], response_model=Student)
async def update_student (student_id: int, student_data: Student,
                       current_user: Annotated[User,Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    updated_student = session.get(Student,student_id)
    if updated_student:
        for key, value in student_data.model_dump(exclude_unset=True).items():
            setattr(updated_student, key, value)
        session.add(updated_student)
        session.commit()
        session.refresh(updated_student)
        return updated_student
    raise HTTPException(status_code = 404, detail = "Student not found!")


#Delete Student
@router.delete("/students/{student_id}", tags = ["students"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int,  current_user: Annotated[User,Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    deleted_student = session.get(Student, student_id)
    if deleted_student:
        session.delete(deleted_student)
        session.commit()
        return {"detail": "student deleted successfully!"}
    raise HTTPException(status_code = 404, detail = "Student not found!")


