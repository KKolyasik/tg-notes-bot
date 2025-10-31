from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.repositories.base import CRUDBase


class CRUDUser(CRUDBase):

    async def get_user_by_tg_id(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> User | None:
        """Получение пользователя по его id в TG."""
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        return user.scalar_one_or_none()

    async def get_chat_id_by_tg_id(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> int | None:
        return await session.scalar(
            select(User.chat_id)
            .where(User.tg_id == tg_id)
        )


user_crud = CRUDUser(User)
