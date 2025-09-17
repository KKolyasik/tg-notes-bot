from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get_object_by_id(self, obj_id: int, session: AsyncSession):
        """Получение объекта по ID."""
        obj = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )

        return obj.scalar_one_or_none()

    async def create_object(
        self,
        data,
        session: AsyncSession,
        user: Optional[User] = None,
    ):
        """"Создание объекта в БД."""
        if user is not None:
            data["user_id"] = user.id
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj
