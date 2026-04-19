from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(self, payload: UserCreate) -> User:
        existing = self.db.query(User).filter(User.email == payload.email).first()
        if existing is not None:
            raise ConflictError("Email is already registered")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")

        token = create_access_token(subject=user.email)
        return TokenResponse(access_token=token, role=user.role)
