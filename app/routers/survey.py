from typing import Annotated
from inspect import currentframe

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from app.dependencies import get_session
from app.db_models import User, Survey, SurveyCategory
from app.format_models import FilterParams
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()


# crud Survey Category
@router.post("/survey_category/add", tags=["survey_category"], response_model=SurveyCategory)
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


@router.put("/survey_category/update", tags=["survey_category"], response_model=SurveyCategory)
async def update_survey_category(survey_category_id: int,
                                 survey_category_data: SurveyCategory,
                                 current_user: Annotated[User, Depends(get_current_user)],
                                 session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION

    update_category_survey = session.get(SurveyCategory, survey_category_id)
    if update_category_survey:
        for key, value in survey_category_data.model_dump(exclude_unset=True).items():
            setattr(update_category_survey, key, value)
        session.add(update_category_survey)
        session.commit()
        session.refresh(update_category_survey)
        return update_category_survey
    raise HTTPException(status_code=404, detail="survey_category not found!")


@router.delete("/survey_category/delete", tags=["survey_category"], response_model=SurveyCategory)
async def delete_survey_category(survey_category_id: int,
                                 current_user: Annotated[User, Depends(get_current_user)],
                                 session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION
    delete_category_survey = session.get(SurveyCategory, survey_category_id)
    if delete_category_survey:
        session.delete(delete_category_survey)
        session.commit()
        return {"detail": "surveyCategory deleted successfully! "}
    raise HTTPException(status_code=404, detail="survey category not found!")


@router.get("/Survey_category/get_all", tags=["survey_category"], response_model=SurveyCategory)
async def get_all_survey_category(current_user: Annotated[User, Depends(get_current_user)],
                                  session: Annotated[Session, Depends(get_session)],
                                  filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(SurveyCategory)

    if filter_query.query:
        query = query.where(or_(SurveyCategory.name.contains(filter_query.query),
                                SurveyCategory.id.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(SurveyCategory, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/survey_category/get", tags=["survey_category"], response_model=SurveyCategory)
async def get_survey_category(survey_category_id: int,
                              current_user: Annotated[User, Depends(get_current_user)],
                              session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION
    survey_category_self = session.get(SurveyCategory, survey_category_id)
    if survey_category_self:
        return survey_category_self
    raise HTTPException(status_code=404, detail="Survey category not found!")


# crud Survey
@router.post("/survey/add", tags=["survey"], response_model=Survey)
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


@router.put("/survey/update/", tags=["survey"], response_model=Survey)
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


@router.delete("/survey/delete", tags=["survey"], response_model=Survey)
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


@router.get("/survey/get_all", tags=["survey"])
async def get_surveys(session: Annotated[Session, Depends(get_session)],
                      current_user: Annotated[User, Depends(get_current_user)],
                      filter_query: Annotated[FilterParams, Query()]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    query = select(Survey)
    if filter_query.query:
        query = query.where(or_(Survey.name.contains(filter_query.query), Survey.id.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(Survey, filter_query.order_by)
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by} ")
    query = query.offset((filter_query.page_size - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


@router.get("/survey/get/{survey_id}", tags=["survey"])
async def get_survey(survey_id: int,
                     current_user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)]):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permission:
            raise CREDENTIALS_EXCEPTION
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")
    return survey
