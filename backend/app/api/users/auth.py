from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.dependencies import get_current_user, get_db
from app.core.auth_security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.identity.department import Department
from app.models.identity.role import Role
from app.models.identity.user import User
from app.schemas.users.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    db:Session=Depends(get_db)
):
    existing_user = db.query(User).filter(User.email==request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    employee_role = db.query(Role).filter(Role.name=='EMPLOYEE').first()
    if not employee_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role is not configured",
        )

    procurement_department = db.query(Department).filter(Department.name=='Procurement').first()

    password_hash = hash_password(request.password)

    user = User(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        password_hash=password_hash,
        role_id=employee_role.id,
        department_id=(
            procurement_department.id
            if procurement_department
            else None
        ),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role.name,
        department=(
            user.department.name
            if user.department
            else None
        ),
        is_active=user.is_active,
    )



@auth_router.post('/login',response_model=TokenResponse)
def login(
    request:LoginRequest,
    db:Session=Depends(get_db)
):
    user = db.query(User).filter(User.email==request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(password=request.password, password_hash=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )



@auth_router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role.name,
        department=(
            current_user.department.name
            if current_user.department
            else None
        ),
        is_active=current_user.is_active,
    )