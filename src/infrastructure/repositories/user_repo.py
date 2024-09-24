"""This module contains the implementation of the user repository."""
from datetime import date, datetime, timedelta
from typing import Sequence


from src.infrastructure.models.user import User
from src.infrastructure.repositories.base import SQLAlchemyRepo


class UserRepo(SQLAlchemyRepo[User]):
    """User repository implementation for SQLAlchemy ORM."""
    
    model = User
    
    async def create_user(self) -> User:
        user = User()
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
