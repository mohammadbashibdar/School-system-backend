from typing import List
from inspect import currentframe
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette import status
from app.dependencies import get_session
from app.db_models import PermissionGroup, User
from app.routers.security import get_current_user, CREDENTIALS_EXCEPTION

router = APIRouter()

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

# Get All Permission Groups
@router.get("/permission-groups/", tags=["permission-groups"], response_model=List[PermissionGroup])
async def get_permission_groups(current_user: User = Depends(get_current_user),
                                session: Session = Depends(get_session)):
    if current_user.permission_group.name != 'full_permission_group':
        if currentframe().f_code.co_name not in current_user.permission_group.permissions:
            raise CREDENTIALS_EXCEPTION
    permission_groups = session.exec(select(PermissionGroup)).all()
    if permission_groups:
        return permission_groups
    raise HTTPException(status_code=404, detail="Permission groups not found!")

# Get Permission Group by ID
@router.get("/permission-groups/{permission_group_id}", tags=["permission-groups"], response_model=PermissionGroup)
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
@router.put("/permission-groups/{permission_group_id}", tags=["permission-groups"], response_model=PermissionGroup)
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
@router.delete("/permission-groups/{permission_group_id}", tags=["permission-groups"], status_code=status.HTTP_204_NO_CONTENT)
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
