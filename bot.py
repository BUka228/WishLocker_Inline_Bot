import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers.inline import router as inline_router
from handlers.callbacks import router as callbacks_router
from handlers.zoo import router as zoo_router
from handlers.places import router as places_router


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(inline_router)
    dp.include_router(callbacks_router)
    dp.include_router(zoo_router)
    dp.include_router(places_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())