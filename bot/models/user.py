from sqlalchemy import BigInteger, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from bot.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    chat_id = Column(BigInteger, index=True, nullable=False)
    username = Column(String(128), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    reminders = relationship("Reminder", back_populates="user")
