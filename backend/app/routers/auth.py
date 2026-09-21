from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import LoginRequest, Token, UserResponse, UserCreate
from backend.app.utils.security import verify_password, create_access_token, hash_password
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        log_audit_event(
            db=db,
            action="USER_LOGIN_FAILED",
            resource_type="USER",
            resource_id=login_data.username,
            details=f"Failed login attempt for username '{login_data.username}'",
            ip_address=request.client.host if request.client else "127.0.0.1"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id}
    )
    
    log_audit_event(
        db=db,
        action="USER_LOGIN_SUCCESS",
        resource_type="USER",
        resource_id=str(user.id),
        details=f"User '{user.username}' successfully authenticated with role '{user.role}'",
        user=user,
        ip_address=request.client.host if request.client else "127.0.0.1"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db=db,
        action="USER_CREATED",
        resource_type="USER",
        resource_id=str(new_user.id),
        details=f"Admin '{current_user.username}' created user '{new_user.username}' with role '{new_user.role}'",
        user=current_user
    )
    return new_user
