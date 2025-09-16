from sqlalchemy import Column, Integer, String

from bot.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True)
    first_name = Column(String(128))
