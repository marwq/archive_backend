"""Unit of Work implementation for SQLAlchemy ORM."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.repositories import (
    UserRepo,
    ChatRepo,
)


class SQLAlchemyUoW:
    """
    A Unit of Work (UoW) implementation using SQLAlchemy for ORM.

    This class manages the lifecycle of database sessions and transaction, providing
    a consistent interface to perform database operations in a transactional context.

    Attributes:
        users (UserRepo): A repository handling user-related database operations.
        session_factory (async_sessionmaker): A factory for creating new SQLAlchemy
        session instances.
        session: The current SQLAlchemy session, initialized during context management.
    """

    user_repo: UserRepo
    chat_repo: ChatRepo

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Initialize the SQLAlchemy Unit of Work with a session factory.

        Args:
            session_factory (async_sessionmaker): A factory for creating new SQLAlchemy
                                                  session instances.
        """
        self.session_factory = session_factory
        self.session: AsyncSession = None

    @property
    def db(self) -> "SQLAlchemyUoW":
        return self

    async def __aenter__(self) -> "SQLAlchemyUoW":
        """
        Enter the runtime context related to this object.

        The context manager creates a new SQLAlchemy session and initializes
        the repositories.

        Returns:
            SQLAlchemyUoW: The instance of the current unit of work.
        """
        if self.session is not None:
            logger.error("Entering uow multiple times")
            return self
        self.session = self.session_factory()
        self.user_repo = UserRepo(self.session)
        self.chat_repo = ChatRepo(self.session)
        return self

    async def __aexit__(self, *args) -> None:
        """
        Exit the runtime context and close the session.

        This method ensures that the session is rolled back and closed properly, even
        if an exception occurs during the transaction.

        Args:
            args: Variable-length argument list.
        """
        await self.session.close()

    async def commit(self) -> None:
        """
        Commit the transaction.

        Attempts to commit the changes made in the session to the database. If an error
        occurs during the commit, a CommitError is raised.

        Raises:
            CommitError: If an SQLAlchemyError occurs during session commit.
        """
        await self.session.commit()

    async def flush(self) -> None:
        """
        Flush the session.

        Attempts to flush the changes made in the session to the database. If an error
        occurs during the flush, a CommitError is raised.

        Raises:
            CommitError: If an SQLAlchemyError occurs during session flush.
        """
        await self.session.flush()

    async def rollback(self) -> None:
        """
        Roll back the transaction.

        Attempts to roll back the changes made in the session. If an error occurs during
        the rollback, a RollbackError is raised.

        Raises:
            RollbackError: If an SQLAlchemyError occurs during session rollback.
        """
        await self.session.rollback()
