from collections.abc import Mapping, Sequence
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from bot.core.db import Base
from bot.models import User

ModelT = TypeVar("ModelT", bound=Base)


class CRUDBase(Generic[ModelT]):

    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def get_object_by_id(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> ModelT | None:
        """Получение объекта по ID."""
        obj = await session.execute(
            select(self.model).where(self.model.id == obj_id),
        )

        return obj.scalar_one_or_none()

    async def create_object(
        self,
        data,
        session: AsyncSession,
        user: User | None = None,
    ) -> ModelT:
        """Создание объекта в БД."""
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
        filters: dict | None = None,
        order_by: Any | None = None,
        limit: int | None = None,
        offset: int | None = None,
        options: Sequence | None = None,
    ) -> list[ModelT]:
        """Получение списка объектов по фильтрам.

        Args:
          - filters - словарь с фильтрами
            (поддерживает в качестве значения итеррируемые объекты)
          - order_by - поле сортировки или сразу SQLAlchemy-выражение
          - limit и offset - пагинация
          - options - дополнительные опции загрузки
        """
        stmt = select(self.model)
        if filters is not None:
            for column, value in self.validate_filters(filters):
                if isinstance(value, (list, tuple, set)):
                    stmt = stmt.where(column.in_(value))
                elif value is None:
                    stmt = stmt.where(column.is_(None))
                else:
                    stmt = stmt.where(column == value)
        if order_by is not None:
            if isinstance(order_by, str):
                stmt = stmt.order_by(self._get_model_column(order_by))
            else:
                stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        if options is not None:
            if not isinstance(options, Sequence) or isinstance(
                options,
                (str, bytes),
            ):
                options = [options]
            for opt in options:
                if opt is not None:
                    stmt = stmt.options(opt)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_obj(
        self,
        db_obj: ModelT,
        data: dict,
        session: AsyncSession,
    ) -> ModelT:
        if not isinstance(data, dict):
            raise ValueError("Unsupported input data")

        for key, value in data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete_obj(self, db_obj: ModelT, session: AsyncSession) -> None:
        await session.delete(db_obj)
        await session.commit()

    def validate_filters(
        self,
        filters: Mapping[str, Any] | None,
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
