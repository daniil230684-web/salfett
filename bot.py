import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://salfett.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("О, здорово, чел. Тестовый режим запущен.")

@dp.message()
async def handle_message(message: types.Message):
    # Бот просто повторит твоё сообщение, не отправляя ничего в OpenRouter
    await message.reply(f"Ты написал: {message.text}. Сервер Render работает!")

async def handle_telegram_webhook(request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Ошибка апдейта: {e}")
    return web.Response(text="OK")

async def handle_root(request):
    return web.Response(text="Бот онлайн!")

async def on_startup(app):
    webhook_url = f"{BASE_URL}/webhook"
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url, drop_pending_updates=True)

def main():
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_post("/webhook", handle_telegram_webhook)
    app.on_startup.append(on_startup)
    
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()