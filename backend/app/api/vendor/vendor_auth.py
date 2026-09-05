from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.dependencies import get_db
from app.core.auth_security import create_access_token, verify_password
from app.models.vendor.vendor_user import VendorUser


class VendorLoginRequest(BaseModel):
    email: EmailStr
    password: str


class VendorTokenResponse(BaseModel):
    access_token: str
    token_type: str
    vendor_id: int
    vendor_name: str


vendor_auth_router = APIRouter(
    prefix="/vendor/auth",
    tags=["Vendor Authentication"],
)


@vendor_auth_router.post("/login", response_model=VendorTokenResponse)
def vendor_login(
    request: VendorLoginRequest,
    db: Session = Depends(get_db),
):
    vendor_user = db.query(VendorUser).filter(
        VendorUser.email == request.email
    ).first()

    if not vendor_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(request.password, vendor_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not vendor_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor account is inactive",
        )

    access_token = create_access_token(subject=str(vendor_user.id))

    return VendorTokenResponse(
        access_token=access_token,
        token_type="bearer",
        vendor_id=vendor_user.vendor_id,
        vendor_name=vendor_user.vendor.name,
    )