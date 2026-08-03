from fastapi import APIRouter, Depends, Request, Response, Cookie
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.errors import UnauthorizedError
from app.core.pagination import page_params, paginate_meta, PageParams
from app.core.roles import Role
from app.features.auth.models import User
from app.features.auth.schemas import (
    LoginRequest, UserOut, CreateUserRequest, ChangePasswordRequest, UserStatusUpdateRequest,
)
from app.features.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])

REFRESH_COOKIE_NAME = "refresh_token"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=True,       # set False only for local http dev if needed
        samesite="strict",
        path="/api/v1/auth",
    )


@router.post("/login")
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token, raw_refresh, user = service.login(
        payload.username, payload.password, request_id=str(getattr(request.state, "request_id", None))
    )
    _set_refresh_cookie(response, raw_refresh)
    return {"success": True, "data": {"access_token": access_token, "user": UserOut.model_validate(user)}}


@router.get("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db),
            refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise UnauthorizedError("No refresh token present.", code="MISSING_REFRESH_TOKEN")
    service = AuthService(db)
    access_token, new_raw = service.refresh(
        refresh_token, request_id=str(getattr(request.state, "request_id", None))
    )
    _set_refresh_cookie(response, new_raw)
    return {"success": True, "data": {"access_token": access_token}}


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db),
            refresh_token: str | None = Cookie(default=None),
            current_user: User = Depends(get_current_user)):
    service = AuthService(db)
    if refresh_token:
        service.logout(refresh_token, current_user, request_id=str(getattr(request.state, "request_id", None)))
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return {"success": True, "data": None}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, request: Request, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    service = AuthService(db)
    service.change_password(current_user, payload.old_password, payload.new_password,
                             request_id=str(getattr(request.state, "request_id", None)))
    return {"success": True, "data": None}


# ---- User administration (Admin only) ----------------------------------

@users_router.post("", dependencies=[Depends(require_role(Role.ADMIN))])
def create_user(payload: CreateUserRequest, request: Request, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    service = AuthService(db)
    user = service.create_user(payload, current_user, request_id=str(getattr(request.state, "request_id", None)))
    return {"success": True, "data": UserOut.model_validate(user)}


@users_router.get("", dependencies=[Depends(require_role(Role.ADMIN))])
def list_users(db: Session = Depends(get_db), pagination: PageParams = Depends(page_params)):
    service = AuthService(db)
    items, total = service.list_users(pagination.page, pagination.page_size)
    return {
        "success": True,
        "data": [UserOut.model_validate(u) for u in items],
        "meta": paginate_meta(pagination.page, pagination.page_size, total),
    }


@users_router.put("/{user_id}/status", dependencies=[Depends(require_role(Role.ADMIN))])
def set_user_status(user_id: str, payload: UserStatusUpdateRequest, request: Request,
                     db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AuthService(db)
    user = service.set_user_status(user_id, payload.is_active, current_user,
                                    request_id=str(getattr(request.state, "request_id", None)))
    return {"success": True, "data": UserOut.model_validate(user)}
