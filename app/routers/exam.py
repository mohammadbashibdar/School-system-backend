from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import session
from sqlmodel import Session, select
from app.dependencies import get_session
from app.db_models import Exam
from app.format_models import FilterParams
from sqlalchemy import or_
from app.db_models import User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION, get_password_hash
from typing import List

router = APIRouter()


# ? raise is not reachable ( use try-catch )
@router.post("/exams/add", tags=["exams"], response_model=Exam)
async def add_exam(exam_add: Exam, current_user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_exam = exam_add.model_validate(exam_add)
        session.add(temp_exam)
        session.commit()
        session.refresh(temp_exam)
        return temp_exam
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error Adding exam")


# ? use filter params
@router.get("/exams/", tags=["exams"], response_model=List[Exam])
async def get_exams(current_user: Annotated[User, Depends(get_current_user)],
                    session: Annotated[Session, Depends(get_session)],
                         filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    exam_read = session.exec(select(Exam)).all()
    if filter_query.query:
        query= exam_read.where(or_(Exam.schedule_id.contains(filter_query.query),
                                       Exam.student_id.contains(filter_query.query)))
    if filter_query.order_by:
        try:
            sort:getattr(Exam, filter_query.order_by)
            query = query.order_by(sort.asc() if filter_query.order_type == "asc" else sort.desc())
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"rollcall not found")
    if not exam_read:
        raise HTTPException(status_code=404, detail=f"exam not found")
    return exam_read

@router.get("/exams/{exams_id}", tags=["exams"], response_model=Exam)
async def read_exam_me(exam_id: int, current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    exam_read = session.get(Exam, exam_id)
    # exam_read = session.exec(select(exam).where(exam.exam_id == exam_id)).first()
    if not exam_read:
        raise HTTPException(status_code=404, detail=f"exam not found")
    return exam_read


@router.put("/exams/{exam_name}", tags=["exams"], response_model=Exam)
async def update_exam(exam_id: int, exam_data: Exam, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    exam_read = session.get(Exam, exam_id)
    if not exam_read:
        raise HTTPException(status_code=404, detail="exam not found")
    for key, value in exam_data.dict(exclude_unset=True).items():
        setattr(exam_read, key, value)
    session.add(exam_read)
    session.commit()
    session.refresh(exam_read)
    return exam_read


@router.delete("/exams/{exam_id}", tags=["exams"], response_model=Exam)
async def delete_exam(exam_id: int, current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    exam_read = session.get(Exam, exam_id)
    if not exam_read:
        raise HTTPException(status_code=404, detail="exam not found")
    session.delete(exam_read)
    session.commit()
    session.refresh(exam_read)
    return {"message": f"exam {exam_id} deleted"}
