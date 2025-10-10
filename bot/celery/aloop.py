import asyncio
from collections.abc import Coroutine
from threading import Thread
from typing import Any

loop: asyncio.AbstractEventLoop | None = None
thread: Thread | None = None


def start_loop() -> None:
    global loop, thread
    if loop is not None:
        return

    loop = asyncio.new_event_loop()

    def runner():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    thread = Thread(target=runner, name="celery-asyncio-loop", daemon=True)
    thread.start()


def stop_loop() -> None:
    global loop, thread
    if loop is None:
        return

    loop.call_soon_threadsafe(loop.stop)

    if thread is not None:
        thread.join(timeout=2)

    loop = None
    thread = None


def run_coro(coro: Coroutine[Any, Any, Any]) -> Any:
    """Выполнить корутину в фоновом loop и дождаться результата (блокирующе).
    """
    if loop is None:
        raise RuntimeError("Async loop is not started")

    fut = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result()
