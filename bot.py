import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# На сервере нет блокировок, подключаемся напрямую!
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Здорово, мелкий! Я наконец-то живой, сижу на бесплатном сервере и готов к работе!")

@dp.message()
async def echo_message(message: types.Message):
    if message.text:
        await message.answer(message.text)

async def main():
    print("Бот успешно запущен на сервере Render!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())