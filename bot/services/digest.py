from datetime import datetime, timedelta

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.schemas.digest import DailyDigest, TopUser
from bot.models.user import User
from bot.models.note import Note, Reminder


async def create_daily_digest(session: AsyncSession) -> DailyDigest:
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)

    new_users_count = (
        await session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.created_at >= start, User.created_at < end)
        )
        or 0
    )

    notes_count = await session.scalar(
        select(func.count())
        .select_from(Note)
    ) or 0

    avg_note_len = await session.scalar(
        select(func.coalesce(func.avg(func.length(Note.title)), 0.0))
    )
    avg_note_len = float(avg_note_len or 0.0)

    dau = (
        await session.scalar(
            select(func.count(func.distinct(Reminder.user_id)))
            .where(
                Reminder.created_at >= start, Reminder.created_at <= end
            )
        )
        or 0
    )

    notes_cnt = func.count(Note.id).label("notes_cnt")
    rows = await session.execute(
        select(User, notes_cnt)
        .outerjoin(User.reminders)
        .group_by(User.id)
        .order_by(desc(notes_cnt))
        .limit(5)
    )
    top_users = [
        TopUser(
            user_id=user.id,
            username=user.username,
            notes_count=int(cnt or 0),
        )
        for (user, cnt) in rows.all()
    ]

    return DailyDigest(
        date=start.date().isoformat(),
        dau=dau,
        new_users=new_users_count,
        notes_count=notes_count,
        avg_note_len=avg_note_len,
        top_users=top_users,
        errors_count=0,
    )
