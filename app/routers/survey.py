from typing import Annotated
from inspect import currentframe

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from app.dependencies import get_session
from app.db_models import User, Survey
from app.format_models import FilterParams
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION


router = APIRouter()

@router.post("/add/survey/", tags=["survey"], response_model=Survey)
async def add_survey(survey: Survey,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permission:
                raise CREDENTIALS_EXCEPTION
        new_survey = Survey.model_validate(survey)
        session.add(new_survey)
        session.commit()
        session.refresh(new_survey)
        return new_survey
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"An Error occurred during adding survey_category:{e}")


@router.put("/update/survey/", tags=["survey"], response_model=Survey)
async def update_survey(survey_id: int,
                        survey_data: Survey,
                        current_user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION

    update_surveys = session.get(Survey, survey_id)
    if update_surveys:
        for key, value in survey_data.model_dump(exclude_unset=True).items():
            setattr(update_surveys, key, value)
        session.add(update_surveys)
        session.commit()
        session.refresh(update_surveys)
        return update_surveys
    raise HTTPException(status_code=404, detail="survey not found")

@router.delete("/delete/survey/", tags=["survey"], response_model=Survey)
async def delete_user(Survey_id: int,
                      current_user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION

    delete_survey = session.get(Survey, Survey_id)
    if delete_survey:
        session.delete(delete_survey)
        session.commit()
        session.refresh(delete_survey)
        return {"details": "survey deleted successfully"}
    raise HTTPException(status_code=404, detail="survey not found")

@router.get("/surveys/", tags=["survey"])
async def get_surveys(session: Annotated[Session, Depends(get_session)],
                      current_user: Annotated[User, Depends(get_current_user)],
                      filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Survey)
    if filter_query.query:
        query = query.where(or_(Survey.name.contains(filter_query.query),Survey.id.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(Survey, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by} ")
    query = query.offset((filter_query.page_size - 1 )* filter_query.page_size) .limit(filter_query.page_size)

    return session.exec(query).all()

@router.get("/surveys/{survey_id}", tags=["survey"])
async def get_survey(survey_id: int,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise  CREDENTIALS_EXCEPTION
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")
    return survey