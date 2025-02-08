from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from app.db_models import Category,User
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe

router = APIRouter()


@router.post("/categories/", tags=["categories"], response_model=Category)
async def add_category(
    category_data: Category,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Add a new category."""
    try:
        if current_user.permission_group.name != "full_permission_group":
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION

        temp_category = Category.model_validate(category_data)
        session.add(temp_category)
        session.commit()
        session.refresh(temp_category)
        return temp_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding category: {e}")


@router.get("/categories/", tags=["categories"], response_model=List[Category])
async def get_categories(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    query: Annotated[str | None, Query()] = None,
):
    """Retrieve all categories."""
    if current_user.permission_group.name != "full_permission_group":
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    statement = select(Category)
    if query:
        statement = statement.where(Category.category_name.contains(query))
    return session.exec(statement).all()


@router.get("/categories/{category_id}", tags=["categories"], response_model=Category)
async def get_category(
    category_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Retrieve a category by ID."""
    if current_user.permission_group.name != "full_permission_group":
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", tags=["categories"], response_model=Category)
async def update_category(
    category_id: int,
    category_data: Category,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update a category's information."""
    if current_user.permission_group.name != "full_permission_group":
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/categories/{category_id}", tags=["categories"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete a category by ID."""
    if current_user.permission_group.name != "full_permission_group":
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"detail": "Category deleted successfully"}
