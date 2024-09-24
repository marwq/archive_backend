import dataclasses
from typing import Generic, NewType, Sequence, TypeVar

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.base import Base

T = TypeVar("T", bound=Base)

IsCreated = NewType("IsCreated", bool)


@dataclasses.dataclass
class SQLAlchemyRepo(Generic[T]):
    model: type[T] = dataclasses.field(init=False)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_item_by_id(self, item_id: int | str) -> T:
        # logger.info("Getting item by id", kwargs={"id": item_id, "model": self.model})

        result = await self._session.get(self.model, item_id)
        return result

    async def select_for_update(self, item_id: int | str) -> T:
        logger.info(
            "Selecting item for update", kwargs={"id": item_id, "model": self.model}
        )

        stmt = (
            select(self.model)
            .where(self.model.id == item_id)
            .with_for_update(key_share=True)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_filter(self, **kwargs) -> T:
        # logger.info("Getting item by filter", kwargs={"model": self.model})

        stmt = select(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def create(self, model: T) -> T:
        # logger.info("Creating item", kwargs={"model": model})
        self._session.add(model)
        return model

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        **kwargs,
    ) -> Sequence[T]:
        # logger.info("Listing items", kwargs={"model": self.model})

        stmt = select(self.model).offset(skip).limit(limit)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by).desc())

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def delete(self, model: T) -> None:
        # logger.info("Deleting item", kwargs={"model": model})

        await self._session.delete(model)

    async def filter_by(
        self,
        limit: int = 100,
        skip: int = 0,
        order_by: str = None,
        **kwargs,
    ) -> Sequence[T]:
        # logger.info("filtering items", kwargs={"model": self.model})

        stmt = select(self.model).offset(skip).limit(limit)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        if order_by:
            stmt = stmt.order_by(getattr(self.model, order_by).desc())

        results = await self._session.execute(stmt)
        return results.scalars().all()

    async def count(self, **kwargs) -> int:
        stmt = select(func.count()).select_from(self.model)

        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await self._session.execute(stmt)
        return result.scalar()

    async def update(self, item_id: int | str, **kwargs) -> None:
        # logger.info(f"Updating item: ID {item_id}, model {self.model}, kwargs {kwargs}")

        stmt = update(self.model).where(self.model.id == item_id).values(**kwargs)
        await self._session.execute(stmt)

    async def get_or_create(self, pk: int | str, **kwargs) -> tuple[T, IsCreated]:
        item = await self.get_item_by_id(item_id=pk)
        if item:
            return item, IsCreated(False)

        item = self.model(id=pk, **kwargs)
        await self.create(item)
        return item, IsCreated(True)

    async def first(self, **kwargs) -> T:
        stmt = select(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await self._session.execute(stmt)
        return result.scalars().first()
