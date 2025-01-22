from typing import List
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette import status
from app.dependencies import get_session
from app.db_models import PermissionGroupPermissionLink, User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()

# Create PermissionGroupPermissionLink
@router.post("/permission-group-links/add", tags=["permission-group-links"], response_model=PermissionGroupPermissionLink)
async def add_permission_group_link(link: PermissionGroupPermissionLink,
                                    current_user: User = Depends(get_current_user),
                                    session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    new_link = PermissionGroupPermissionLink.model_validate(link)
    session.add(new_link)
    session.commit()
    session.refresh(new_link)
    return new_link

# Get All PermissionGroupPermissionLinks
@router.get("/permission-group-links/", tags=["permission-group-links"], response_model=List[PermissionGroupPermissionLink])
async def get_permission_group_links(current_user: User = Depends(get_current_user),
                                     session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    links = session.exec(select(PermissionGroupPermissionLink)).all()
    if links:
        return links
    raise HTTPException(status_code=404, detail="Permission group links not found!")

# Get PermissionGroupPermissionLink by ID
@router.get("/permission-group-links/{link_id}", tags=["permission-group-links"], response_model=PermissionGroupPermissionLink)
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
@router.put("/permission-group-links/{link_id}", tags=["permission-group-links"], response_model=PermissionGroupPermissionLink)
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
@router.delete("/permission-group-links/{link_id}", tags=["permission-group-links"], status_code=status.HTTP_204_NO_CONTENT)
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
