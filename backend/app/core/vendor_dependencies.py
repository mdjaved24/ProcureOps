from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.auth_security import decode_access_token
from app.models.vendor.vendor_user import VendorUser


security = HTTPBearer()


def get_current_vendor_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> VendorUser:
    """
    Get current vendor user from JWT token.
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        vendor_user_id = int(subject)
        vendor_user = db.query(VendorUser).filter(VendorUser.id == vendor_user_id).first()
        
        if not vendor_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Vendor user not found"
            )
        
        if not vendor_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendor account is inactive"
            )
        
        return vendor_user
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )