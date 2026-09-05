from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.core.dependencies import get_db, get_current_user
from app.core.authorization import require_permission
from app.core.auth_security import hash_password
from app.models.identity.user import User
from app.models.identity.role import Role
from app.models.identity.department import Department
from app.models.vendor.vendor import Vendor
from app.models.vendor.vendor_user import VendorUser
from app.schemas.users.auth import UserResponse


# ============================================================
# SCHEMAS
# ============================================================

class UserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)
    role_id: int
    department_id: Optional[int] = None
    vendor_id: Optional[int] = None  # Only for VENDOR role


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    vendor_id: Optional[int] = None


class UserListResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    role: str
    role_id: int
    department: Optional[str]
    department_id: Optional[int]
    vendor_id: Optional[int]
    vendor_name: Optional[str]
    is_active: bool
    created_at: str


class VendorDropdownResponse(BaseModel):
    id: int
    vendor_code: str
    name: str
    email: str
    status: str


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool


admin_user_router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - User Management"],
)


# ============================================================
# CREATE USER
# ============================================================

@admin_user_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Check if role exists
    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Check if department exists (if provided)
    department = None
    if request.department_id:
        department = db.query(Department).filter(Department.id == request.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # If role is VENDOR, vendor_id is required
    if role.name.upper() == "VENDOR" and not request.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor ID is required for VENDOR role"
        )

    # Check vendor exists (if provided)
    vendor = None
    if request.vendor_id:
        vendor = db.query(Vendor).filter(Vendor.id == request.vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

    # Create user
    user = User(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        role_id=request.role_id,
        department_id=request.department_id,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # If role is VENDOR, create VendorUser entry
    if role.name.upper() == "VENDOR" and request.vendor_id:
        vendor_user = VendorUser(
            vendor_id=request.vendor_id,
            user_id=user.id,
            email=request.email,
            password_hash=user.password_hash,
            full_name=request.full_name,
            is_active=True,
        )
        db.add(vendor_user)

    db.commit()
    db.refresh(user)

    # Return properly formatted response
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role.name if user.role else None,
        department=user.department.name if user.department else None,
        is_active=user.is_active,
    )


# ============================================================
# LIST USERS
# ============================================================

@admin_user_router.get(
    "",
    response_model=List[UserListResponse],
)
def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role_id: Optional[int] = Query(None, description="Filter by role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    query = db.query(User)

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    # Role filter
    if role_id:
        query = query.filter(User.role_id == role_id)

    users = query.offset(skip).limit(limit).all()

    result = []
    for user in users:
        # Get vendor info if user has vendor role
        vendor_user = db.query(VendorUser).filter(VendorUser.user_id == user.id).first()
        vendor_name = None
        vendor_id = None
        if vendor_user and vendor_user.vendor:
            vendor_name = vendor_user.vendor.name
            vendor_id = vendor_user.vendor_id

        result.append(UserListResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.role.name if user.role else None,
            role_id=user.role_id,
            department=user.department.name if user.department else None,
            department_id=user.department_id,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
        ))

    return result


# ============================================================
# GET USER BY ID
# ============================================================

@admin_user_router.get(
    "/{user_id}",
    response_model=UserListResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    vendor_user = db.query(VendorUser).filter(VendorUser.user_id == user.id).first()
    vendor_name = None
    vendor_id = None
    if vendor_user and vendor_user.vendor:
        vendor_name = vendor_user.vendor.name
        vendor_id = vendor_user.vendor_id

    return UserListResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role.name if user.role else None,
        role_id=user.role_id,
        department=user.department.name if user.department else None,
        department_id=user.department_id,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


# ============================================================
# UPDATE USER
# ============================================================

@admin_user_router.put(
    "/{user_id}",
    response_model=UserListResponse,
)
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.email is not None:
        user.email = request.email
    if request.phone is not None:
        user.phone = request.phone
    if request.role_id is not None:
        role = db.query(Role).filter(Role.id == request.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        user.role_id = request.role_id
    if request.department_id is not None:
        user.department_id = request.department_id
    if request.is_active is not None:
        user.is_active = request.is_active

    db.commit()
    db.refresh(user)

    vendor_user = db.query(VendorUser).filter(VendorUser.user_id == user.id).first()
    vendor_name = None
    vendor_id = None
    if vendor_user and vendor_user.vendor:
        vendor_name = vendor_user.vendor.name
        vendor_id = vendor_user.vendor_id

    return UserListResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role.name if user.role else None,
        role_id=user.role_id,
        department=user.department.name if user.department else None,
        department_id=user.department_id,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


# ============================================================
# DELETE USER
# ============================================================

@admin_user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Don't allow deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Delete vendor user association if exists
    vendor_user = db.query(VendorUser).filter(VendorUser.user_id == user.id).first()
    if vendor_user:
        db.delete(vendor_user)

    db.delete(user)
    db.commit()


# ============================================================
# GET ROLES DROPDOWN
# ============================================================

@admin_user_router.get(
    "/roles/dropdown",
    response_model=List[RoleResponse],
)
def get_roles_dropdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    roles = db.query(Role).filter(Role.is_active == True).order_by(Role.name).all()
    return roles


# ============================================================
# GET VENDORS DROPDOWN
# ============================================================

@admin_user_router.get(
    "/vendors/dropdown",
    response_model=List[VendorDropdownResponse],
)
def get_vendors_dropdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("admin:users")
    ),
):
    vendors = db.query(Vendor).filter(
        Vendor.status == 'ACTIVE'
    ).order_by(Vendor.name).all()
    
    return [
        VendorDropdownResponse(
            id=v.id,
            vendor_code=v.vendor_code,
            name=v.name,
            email=v.email,
            status=v.status,
        )
        for v in vendors
    ]