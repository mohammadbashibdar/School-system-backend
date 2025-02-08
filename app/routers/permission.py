from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from app.db_models import Permission, User, PermissionGroup, PermissionGroupPermissionLink
from app.dependencies import get_session
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION
from inspect import currentframe
from app.format_models import FilterParams
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

router = APIRouter()


# ? merge with the two other permission related routers
@router.get("/permission/get", tags=["permission"])
async def get_permission(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION

    # Define the base query
    query = select(Permission)

    if filter_query.query:
        query = query.where(or_(Permission.id.contains(filter_query.query),
                                Permission.name.contains(filter_query.query)))  # Filter by name or email_address

    if filter_query.order_by:
        try:
            sort_column = getattr(Permission, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


# added all permission_group here

# Create Permission Group
@router.post("/permission-groups/add", tags=["permission-groups"], response_model=PermissionGroup)
async def add_permission_group(permission_group: PermissionGroup,
                               current_user: User = Depends(get_current_user),
                               session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    new_permission_group = PermissionGroup.model_validate(permission_group)
    session.add(new_permission_group)
    session.commit()
    session.refresh(new_permission_group)
    return new_permission_group


# ? filter params
# Get All Permission Groups
@router.get("/permission-groups/get", tags=["permission-groups"], response_model=List[PermissionGroup])
async def get_permission_groups(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()],
):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
        permission_groups = session.exec(select(PermissionGroup)).all()
        if permission_groups:
            return permission_groups
        raise HTTPException(status_code=404, detail="Permission groups not found!")

    # Define the base query
    query = select(PermissionGroup)
    if filter_query.query:
        query = query.where(or_(PermissionGroup.id.contains(filter_query.query),
                                PermissionGroup.name.contains(filter_query.query)))
    if filter_query.order_by:
        try:
            sort_column = getattr(PermissionGroup, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


# Get Permission Group by ID
@router.get("/permission-groups/get{permission_group_id}", tags=["permission-groups"], response_model=PermissionGroup)
async def get_permission_group(permission_group_id: int, current_user: User = Depends(get_current_user),
                               session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    permission_group = session.get(PermissionGroup, permission_group_id)
    if permission_group:
        return permission_group
    raise HTTPException(status_code=404, detail="Permission group not found!")


# Update Permission Group
@router.put("/permission-groups/update{permission_group_id}", tags=["permission-groups"],
            response_model=PermissionGroup)
async def update_permission_group(permission_group_id: int, permission_group_data: PermissionGroup,
                                  current_user: User = Depends(get_current_user),
                                  session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    permission_group = session.get(PermissionGroup, permission_group_id)
    if permission_group:
        for key, value in permission_group_data.model_dump(exclude_unset=True).items():
            setattr(permission_group, key, value)
        session.add(permission_group)
        session.commit()
        session.refresh(permission_group)
        return permission_group
    raise HTTPException(status_code=404, detail="Permission group not found!")


# Delete Permission Group
@router.delete("/permission-groups/delete{permission_group_id}", tags=["permission-groups"],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group(permission_group_id: int, current_user: User = Depends(get_current_user),
                                  session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    permission_group = session.get(PermissionGroup, permission_group_id)
    if permission_group:
        session.delete(permission_group)
        session.commit()
        return {"detail": "Permission group deleted successfully!"}
    raise HTTPException(status_code=404, detail="Permission group not found!")


# added all permission_group_permission_link here


# Create PermissionGroupPermissionLink
@router.post("/permission-group-links/add", tags=["permission-group-links"],
             response_model=PermissionGroupPermissionLink)
async def post_permission_group_link(
        link: PermissionGroupPermissionLink,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    try:
        if current_user.permission_group.name != 'full_permission_group':
            if currentframe().f_code.co_name not in current_user.permission_group.permissions:
                raise CREDENTIALS_EXCEPTION
        new_link = PermissionGroupPermissionLink.model_validate(link)
        session.add(new_link)
        session.commit()
        session.refresh(new_link)
        return new_link
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding PermissionGroupPermissionLink: {e}")


# Get All PermissionGroupPermissionLinks
@router.get("/permission-group-links/get", tags=["permission-group-links"],
            response_model=List[PermissionGroupPermissionLink])
async def get_permission_group_links(

        session: Annotated[Session, Depends(get_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        filter_query: Annotated[FilterParams, Query()]

):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
        links = session.exec(select(PermissionGroupPermissionLink)).all()
        if links:
            return links
        raise HTTPException(status_code=404, detail="Permission group links not found!")

    # Define the base query
    query = select(PermissionGroupPermissionLink)

    if filter_query.query:
        query = query.where(or_(PermissionGroupPermissionLink.id.contains(filter_query.query),
                                PermissionGroupPermissionLink.name.contains(filter_query.query)))

    if filter_query.order_by:
        try:
            sort_column = getattr(PermissionGroupPermissionLink, filter_query.order_by)  # Get the field from the model
            query = query.order_by(sort_column.asc() if filter_query.order_type == "asc" else sort_column.desc())
        except AttributeError:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {filter_query.order_by}")

    query = query.offset((filter_query.page_number - 1) * filter_query.page_size).limit(filter_query.page_size)

    return session.exec(query).all()


# Get PermissionGroupPermissionLink by ID
@router.get("/permission-group-links/get{link_id}", tags=["permission-group-links"],
            response_model=PermissionGroupPermissionLink)
async def get_permission_group_link(link_id: int, current_user: User = Depends(get_current_user),
                                    session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    link = session.get(PermissionGroupPermissionLink, link_id)
    if link:
        return link
    raise HTTPException(status_code=404, detail="Permission group link not found!")


# Update PermissionGroupPermissionLink
@router.put("/permission-group-links/update{link_id}", tags=["permission-group-links"],
            response_model=PermissionGroupPermissionLink)
async def update_permission_group_link(link_id: int, link_data: PermissionGroupPermissionLink,
                                       current_user: User = Depends(get_current_user),
                                       session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    link = session.get(PermissionGroupPermissionLink, link_id)
    if link:
        for key, value in link_data.model_dump(exclude_unset=True).items():
            setattr(link, key, value)
        session.add(link)
        session.commit()
        session.refresh(link)
        return link
    raise HTTPException(status_code=404, detail="Permission group link not found!")


# Delete PermissionGroupPermissionLink
@router.delete("/permission-group-links/delete{link_id}", tags=["permission-group-links"],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group_link(link_id: int, current_user: User = Depends(get_current_user),
                                       session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    link = session.get(PermissionGroupPermissionLink, link_id)
    if link:
        session.delete(link)
        session.commit()
        return {"detail": "Permission group link deleted successfully!"}
    raise HTTPException(status_code=404, detail="Permission group link not found!")
