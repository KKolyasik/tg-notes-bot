import asyncio
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.core.config import settings
from bot.core.db import SessionFactory
from bot.models import Reminder
from bot.celery.utils import create_message, make_bot


@shared_task()
def check_reminders(window: int):
    """
    Проверяет БД каждую минуту, чтобы запланировать отправку.

    Args:
        - window (время в минутах за которое нужно запланировать)
    """
    asyncio.run(_check_reminders(window))


async def _check_reminders(window: int):
    now = datetime.now(timezone.utc)
    until = now + timedelta(minutes=window)
    async with SessionFactory() as session:
        stmt = (
            select(Reminder)
            .options(selectinload(Reminder.note))
            .where(Reminder.status == "pending")
            .where(Reminder.scheduled_at >= now)
            .where(Reminder.scheduled_at <= until)
            .order_by(Reminder.scheduled_at.asc())
            .with_for_update(skip_locked=True)
        )

        reminders = await session.execute(stmt)
        reminders = reminders.scalars().all()

        for reminder in reminders:
            message = create_message(reminder.note.title, reminder.note.body)
            task_id = (
                "reminder:"
                f"{reminder.id}:"
                f"{int(reminder.scheduled_at.timestamp())}"
            )

            send_reminder.apply_async(
                (
                    reminder.id,
                    reminder.chat_id,
                    message,
                ),
                eta=reminder.scheduled_at,
                task_id=task_id,
                queue="reminders",
            )

            reminder.status = "queued"
            reminder.celery_task_id = task_id

        await session.commit()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_reminder(reminder_id: int, chat_id: int, message: str):
    """Таска на отправку уведомлений в тг."""
    asyncio.run(_send_reminder(reminder_id, chat_id, message))


async def _send_reminder(reminder_id: int, chat_id: int, message: str):
    async with SessionFactory() as session:

        stmt = (
            select(Reminder)
            .where(Reminder.id == reminder_id)
            .with_for_update(skip_locked=True)
        )

        reminder = await session.execute(stmt)
        reminder = reminder.scalar_one_or_none()

        if reminder is None:
            return
        if reminder.status == "sent":
            return

        bot = make_bot(settings.BOT_TOKEN)
        try:
            await bot.send_message(chat_id, message)
        finally:
            await bot.session.close()

        reminder.status = "sent"
        reminder.sent_at = datetime.now(timezone.utc)

        await session.commit()
