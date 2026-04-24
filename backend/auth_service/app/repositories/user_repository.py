"""Repositorio User: unica puerta de entrada a la tabla `users`."""
from typing import Optional

from sqlalchemy.orm import Session

from auth_service.app.entities.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
