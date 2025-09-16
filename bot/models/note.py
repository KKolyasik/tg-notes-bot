from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    Index,
    func,
)

from bot.core.db import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        index=True,
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
    next_run_at = Column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    status = Column(
        Enum(
            "scheduled",
            "sent",
            "cancelled",
            "failed",
            name="reminder_status",
        ),
        server_default="scheduled",
        index=True,
        nullable=False,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    fail_count = Column(Integer, server_default="0", nullable=False)
    last_error = Column(Text, nullable=True)

    rrule = Column(
        String(255), nullable=True
    )

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


Index(
    "ix_reminders_due",
    Reminder.status,
    Reminder.next_run_at,
    postgresql_where=(Reminder.status == "scheduled"),
)
