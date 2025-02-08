from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlmodel import Session, select, update, delete, or_

from app.db_models import Lesson, User, Course, Category

from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams

router = APIRouter()


@router.post("/lessons/add", tags=["lessons"], response_model=Lesson)
async def post_lesson(lesson1: Lesson,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]

                      ):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_lesson = Lesson.model_validate(lesson1)
        session.add(temp_lesson)
        session.commit()
        session.refresh(temp_lesson)
        return temp_lesson
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while adding lesson: {e}")


@router.get("/lessons/", tags=["lessons"])
async def get_lessons(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Lesson)

    if filter_query.query:
        query = query.where(Lesson.lesson_name.contains(filter_query.query))  # Filter by name

    if filter_query.order_by:
        try:
            sort_column = getattr(Lesson, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/lessons/{lesson_id}", tags=["lessons"], response_model=Lesson)
async def get_lesson(lesson_id: int,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    course2 = session.get(Lesson, lesson_id)
    if not course2:
        raise HTTPException(status_code=404, detail="lesson not found")
    return course2


@router.put("/lessons/{lesson_id}", tags=["lessons"], response_model=Lesson)
async def update_lesson(
        lesson_id: int, course_data: Lesson, current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    lesson3 = session.get(Lesson, lesson_id)
    if not lesson3:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    for key, value in course_data.dict(exclude_unset=True).items():
        setattr(lesson3, key, value)
    session.add(lesson3)
    session.commit()
    session.refresh(lesson3)
    return lesson3


@router.delete("/lessons/{lesson_id}", tags=["lessons"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(lesson_id: int, current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    lesson0 = session.get(Lesson, lesson_id)
    if not lesson0:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    session.delete(lesson0)
    session.commit()
    return {"detail": "Lesson deleted successfully."}


"""================================================================================================================="""
"""==============================================Category endpoints================================================="""
"""================================================================================================================="""


@router.post("/categories/add", tags=["categories"], response_model=Category)
async def add_category(category1: Category,
                       current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]

                       ):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        temp_lesson = Lesson.model_validate(category1)
        session.add(temp_lesson)
        session.commit()
        session.refresh(temp_lesson)
        return temp_lesson
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while adding category: {e}")


@router.get("/categories/", tags=["categories"])
async def get_categories(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Category)

    if filter_query.query:
        query = query.where(Category.category_name.contains(filter_query.query))  # Filter by name

    if filter_query.order_by:
        try:
            sort_column = getattr(Category, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()

@router.get("/categories/{category_id}", tags=["categories"], response_model=Category)
async def get_category(category_id: int,
                       current_user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    category2 = session.get(Lesson, category_id)
    if not category2:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category2


@router.put("/categories/{category_id}", tags=["categories"], response_model=Category)
async def update_category(
        lesson_id: int, course_data: Lesson, current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    category3 = session.get(Lesson, lesson_id)
    if not category3:
        raise HTTPException(status_code=404, detail="Category not found.")
    for key, value in course_data.dict(exclude_unset=True).items():
        setattr(category3, key, value)
    session.add(category3)
    session.commit()
    session.refresh(category3)
    return category3


@router.delete("/categories/{category_id}", tags=["categories"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, current_user: Annotated[User, Depends(get_current_user)],
                          session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    category0 = session.get(Lesson, category_id)
    if not category0:
        raise HTTPException(status_code=404, detail="category not found.")
    session.delete(category0)
    session.commit()
    return {"detail": "Category deleted successfully."}
