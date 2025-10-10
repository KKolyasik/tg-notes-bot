from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, relationship

from bot.core.db import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    reminder: Mapped["Reminder"] = relationship(
        "Reminder",
        back_populates="note",
        lazy="selectin",
        uselist=False,
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        index=True,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chat_id = Column(BigInteger, index=True, nullable=False)

    scheduled_at = Column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    status = Column(
        Enum(
            "scheduled",
            "sent",
            "queued",
            name="reminder_status",
        ),
        server_default="scheduled",
        index=True,
        nullable=False,
    )
    celery_task_id = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    note: Mapped["Note"] = relationship(
        "Note",
        back_populates="reminder",
        uselist=False,
        lazy="selectin",
    )
    user = relationship("User", back_populates="reminders")
