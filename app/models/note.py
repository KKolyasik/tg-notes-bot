from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)

from app.core.db import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title = Column(String(200))
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
