from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.orm import relationship

from bot.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    first_name = Column(String(128))
    reminders = relationship("Reminder", back_populates="user")
