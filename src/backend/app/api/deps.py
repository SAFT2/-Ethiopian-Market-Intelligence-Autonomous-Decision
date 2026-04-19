from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token")

    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise UnauthorizedError("Invalid or expired token")

    user = db.query(User).filter(User.email == subject).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User is not authorized")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)

    def _check_role(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise UnauthorizedError("Insufficient permissions")
        return user

    return _check_role
