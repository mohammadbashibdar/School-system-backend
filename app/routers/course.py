from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, update, delete, or_
from app.db_models import Course, User, Enrollment, Student, Presenting
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams

router = APIRouter()


@router.post("/courses/add", tags=["courses"], response_model=Course)
async def post_course(course1: Course,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_course = Course.model_validate(course1)
        session.add(temp_course)
        session.commit()
        session.refresh(temp_course)
        return temp_course
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while adding course: {e}")


@router.get("/courses/", tags=["courses"])
async def get_courses(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):

    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Course)

    if filter_query.query:
        query = query.where(Course.course_name.contains(filter_query.query))  # Filter by name

    if filter_query.order_by:
        try:
            sort_column = getattr(Course, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/course/{course_id}", tags=["course"], response_model=List[Course])
async def get_students_by_course(
        course_id: int,
        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.permission_group.name != "full_permission_group":
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # statement = (
    #     select(Student.name)
    #     .join(Enrollment, Enrollment.student_id == Student.id)
    #     .join(Presenting, Presenting.id == Enrollment.presenting_id)
    #     .where(Presenting.course_id == course_id)
    # )
    # students = session.exec(statement).all()
    students = (
        session.query(Student)
        .filter(Student.enrollments.any(Presenting.has(course_id=course_id)))
        .all()
    )

    if not students:
        raise HTTPException(status_code=404, detail="No students found for this course")
    return students


@router.get("/courses/{course_id}", tags=["courses"], response_model=Course)
async def get_course(course_id: int,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    """Retrieve a course by ID."""
    course2 = session.get(Course, course_id)
    if not course2:
        raise HTTPException(status_code=404, detail="Course not found")
    return course2


@router.put("/courses/{course_id}", tags=["courses"], response_model=Course)
async def update_course(
        course_id: int, course_data: Course, current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    course3 = session.get(Course, course_id)
    if not course3:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in course_data.dict(exclude_unset=True).items():
        setattr(course3, key, value)
    session.add(course3)
    session.commit()
    session.refresh(course3)
    return course3


@router.delete("/courses/{course_id}", tags=["courses"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    course0 = session.get(Course, course_id)
    if not course0:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course0)
    session.commit()
    return {"detail": "Course deleted successfully"}
