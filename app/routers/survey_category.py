from typing import Annotated
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from app.dependencies import get_session
from app.db_models import User, Survey, SurveyCategory
from app.format_models import FilterParams
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()

@router.post("/add/category_survey", tags=["survey_category"], response_model=SurveyCategory)
async def add_survey_category(survey_category: SurveyCategory,
                              current_user: Annotated[User, Depends(get_current_user)],
                              session: Annotated[Session, Depends(get_session)]):
    try:
        if current_user.permission_group != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissiond:
                raise CREDENTIALS_EXCEPTION
        new_survey_category = SurveyCategory.model_validate(survey_category)
        session.add(new_survey_category)
        session.commit()
        session.refresh(new_survey_category)
        return new_survey_category
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"An Error occurred during adding survey_category:{e}")


@router.put("/update/survey_category", tags= ["survey_category"], response_model=SurveyCategory)
async def update_survey_category(survey_category_id: int,
                                 survey_category_data: SurveyCategory,
                                 current_user: Annotated[User, Depends(get_current_user)],
                                 session : Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in  current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION

    update_category_survey = session.get(SurveyCategory, survey_category_id)
    if update_category_survey:
        for key, value in survey_category_data.model_dump(exclude_unset=True).items():
            setattr(update_category_survey, key, value)
        session.add(update_category_survey)
        session.commit()
        session.refresh(update_category_survey)
        return update_category_survey
    raise  HTTPException(status_code=404, detail="survey_category not found!")


@router.delete("/delete/survey_category", tags=["survey_category"], response_model=SurveyCategory)
async def delete_survey_category(survey_category_id: int,
                                 current_user: Annotated[User, Depends(get_current_user)],
                                 session: Annotated[Session, get_session]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION
    delete_category_survey = session.get(SurveyCategory, survey_category_id)
    if delete_category_survey:
        session.delete(delete_category_survey)
        session.commit()
        return {"detail": "surveyCategory deleted successfully! "}
    raise HTTPException(status_code=404, detail="survey category not found!")


@router.get("/Survey_category/", tags=["survey_category"], response_model=SurveyCategory)
async def get_all_survey_category(current_user: Annotated[User, Depends(get_current_user)],
                                  session: Annotated[Session, Depends(get_session)],
                                  filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = Survey(SurveyCategory)
    if filter_query.query:
        query = query.where(or_(SurveyCategory.name.contains(filter_query.query),
                                SurveyCategory.id.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(SurveyCategory, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number -1 ) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/get/survey_category/", tags=["survey_category"], response_model=SurveyCategory)
async def get_survey_category(survey_category_id: int,
                              current_user:Annotated[User, Depends(get_current_user)],
                              session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION
    survey_category_self = session.get(SurveyCategory, survey_category_id)
    if survey_category_self:
        return survey_category_self
    raise HTTPException(status_code=404, detail="Survey category not found!")


