from typing import Any, List, Mapping, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute
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
        """ "Создание объекта в БД."""
        if user is not None:
            data["user_id"] = user.id
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_objects(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[Sequence] = None
    ) -> List[Any]:
        """
        Получение списка объектов по фильтрам.

        Args:
          - filters - словарь с фильтрами
            (поддерживает в качестве значения итеррируемые объекты)
          - order_by - поле сортировки или сразу SQLAlchemy-выражение
          - limit и offset - пагинация
          - options - дополнительные опции загрузки
        """
        stmt = select(self.model)
        if filters:
            for column, value in self.validate_filters(filters):
                if isinstance(value, (list, tuple, set)):
                    stmt = stmt.where(column.in_(value))
                elif value is None:
                    stmt = stmt.where(column.is_(None))
                else:
                    stmt = stmt.where(column == value)
        if order_by:
            if isinstance(order_by, str):
                stmt = stmt.order_by(self._get_model_column(order_by))
            else:
                stmt = stmt.order_by(order_by)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        if options:
            if not isinstance(options, Sequence):
                options = [options]
            for option in options:
                stmt = stmt.options(option)
        result = await session.execute(stmt)
        return result.scalars().all()

    def validate_filters(
        self,
        filters: Optional[Mapping[str, Any]],
    ) -> list[tuple[InstrumentedAttribute, Any]]:
        if not filters:
            return []
        validated: list[tuple[InstrumentedAttribute, Any]] = []

        for field, value in filters.items():
            validated.append((self._get_model_column(field), value))
        return validated

    def _get_model_column(self, field: str) -> InstrumentedAttribute:
        column = getattr(self.model, field, None)
        if not isinstance(column, InstrumentedAttribute):
            raise ValueError(f"Unsupported filter field `{field}`")
        return column
