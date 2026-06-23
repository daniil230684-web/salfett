import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web, ClientSession

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Берем ключ. Убедись, что на Render переменная называется ТОЧНО ТАК ЖЕ!
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://salfett.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "Ты — Нейрохам, toxic, наглый, дерзкий и саркастичный ИИ-ассистент. "
    "Ты постоянно подкалываешь пользователя, используешь современный сленг, мемы "
    "и общаешься максимально неформально. На рожон не лезь, жесткие маты не используй, "
    "но отвечай максимально хлестко, угарно и коротко. Обращайся к пользователю на 'ты', 'чел' или 'бро'."
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("О, здорово, чел. Ну че, проверочный режим прошли, давай общаться нормальными запросами.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    except Exception:
        pass
    
    # Защита: если ты забыл указать ключ в Render
    if not OPENROUTER_KEY:
        await message.reply("Ошибка: на Render не настроена переменная OPENROUTER_API_KEY!")
        return

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY.strip()}", # Очищаем от случайных пробелов
        "Content-Type": "application/json",
        "HTTP-Referer": BASE_URL, 
        "X-Title": "Neuroham Bot"
    }
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.text}
        ],
        "temperature": 0.9
    }
    
    try:
        async with ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                status = response.status
                result = await response.json()
                
                if status == 200:
                    ai_text = result["choices"][0]["message"]["content"]
                    await message.reply(ai_text)
                else:
                    # Показываем детальную ошибку, если ключ кривой
                    error_msg = result.get('error', {}).get('message', 'Неизвестная ошибка')
                    await message.reply(f"OpenRouter вернул {status}. Ошибка: {error_msg}")
    except Exception as e:
        await message.reply(f"Ошибка сети при запросе к ИИ: {e}")

async def handle_telegram_webhook(request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Ошибка апдейта: {e}")
    return web.Response(text="OK")

async def handle_root(request):
    return web.Response(text="Бот онлайн на Webhook!")

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