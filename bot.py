import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("Переменная окружения TOKEN не задана")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("hello"))
async def cmd_hello(message: types.Message):
    await message.answer("привет")


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Напиши /hello 🙂")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
