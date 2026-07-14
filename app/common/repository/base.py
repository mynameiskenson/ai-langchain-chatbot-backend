from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

model_type = TypeVar("model_type")


class BaseRepository(Generic[model_type]):
    def __init__(self, db: AsyncSession, model: model_type):
        self.db = db
        self.model = model

    async def list(self) -> list[model_type]:
        stmt = select(self.model)
        result = await self.db.scalars(stmt)
        return result.all()

    async def get(self, id: int) -> model_type:
        stmt = select(self.model).filter(self.model.id == id)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, entity: model_type) -> model_type:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def create_many(self, entities: list[model_type]) -> list[model_type]:
        self.db.add_all(entities)
        await self.db.flush()
        for entity in entities:
            await self.db.refresh(entity)
        return entities

    async def update(self, entity: model_type, obj_in: dict) -> model_type:
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