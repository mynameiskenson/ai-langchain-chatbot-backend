from __future__ import annotations

from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

    async def list(self) -> list[ModelType]:
        stmt = select(self.model)
        result = await self.db.scalars(stmt)
        return result.all()

    async def get(self, id: int) -> ModelType:
        stmt = select(self.model).filter(self.model.id == id)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def create_many(self, entities: list[ModelType]) -> list[ModelType]:
        self.db.add_all(entities)
        await self.db.flush()
        for entity in entities:
            await self.db.refresh(entity)
        return entities

    async def update(self, entity: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(entity, field, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, id: int) -> None:
        entity = await self.get(id)
        if entity:
            await self.db.delete(entity)
            await self.db.flush()