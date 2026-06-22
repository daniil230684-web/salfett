import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Берем токен из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Здорово! Я снова живой и на связи. Пока работаю в режиме эха!")

@dp.message()
async def handle_message(message: types.Message):
    # Просто дублируем сообщение обратно
    await message.answer(message.text)

async def main():
    print("Бот успешно запущен на сервере Render!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())