import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web, ClientSession

BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    await message.answer("О, здорово, чел. Ну и зачем ты меня запустил? Ладно, валяй, попробуй удивить мои процессоры.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    except Exception:
        pass
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": BASE_URL, 
        "X-Title": "Neuroham Bot"
    }
   data = {
        "model": "meta-llama/llama-3-8b-instruct:free",  # Железобетонная бесплатная модель
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
                    print(f"Ошибка OpenRouter: {status} - {result}")
                    await message.reply(f"OpenRouter вернул ошибку {status}. Мозги плавятся!")
    except Exception as e:
        print(f"Ошибка сети: {e}")
        await message.reply("Блин, связь с сервером потеряна.")

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
    # Очищаем старый хвост принудительно перед установкой нового вебхука
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    print(f"Вебхук успешно привязан к: {webhook_url}")

def main():
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_post("/webhook", handle_telegram_webhook)
    app.on_startup.append(on_startup)
    
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()