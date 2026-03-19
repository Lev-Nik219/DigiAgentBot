import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import common, analysis, factcheck, transcribe, monitor, summarize
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)

async def main():
    # Запускаем Flask-сервер в фоне для поддержания активности
    keep_alive()
    # Небольшая задержка, чтобы сервер успел запуститься
    await asyncio.sleep(2)

    session = AiohttpSession(timeout=300)
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(analysis.router)
    dp.include_router(factcheck.router)
    dp.include_router(transcribe.router)
    dp.include_router(monitor.router)
    dp.include_router(summarize.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())