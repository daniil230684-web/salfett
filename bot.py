import os
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import AsyncOpenAI
from aiohttp import web

# Вытаскиваем ключи из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# ЖЕСТКИЙ ФИКС: создаем чистый клиент httpx без поддержки прокси
# Это на 100% уберет ошибку "unexpected keyword argument 'proxies'"
custom_http_client = httpx.AsyncClient(proxies=None) if hasattr(httpx, 'AsyncClient') else None

# Подключаем OpenRouter для ИИ
ai_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
    http_client=custom_http_client # Передаем наш чистый клиент
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настройка характера Нейрохама
SYSTEM_PROMPT = (
    "Ты — Нейрохам, токсичный, наглый, дерзкий и саркастичный ИИ-ассистент. "
    "Ты постоянно подкалываешь пользователя, используешь современный сленг, мемы "
    "и общаешься максимально неформально. На рожон не лезь, жесткие маты не используй (чтобы ТГ не забанил), "
    "но отвечай максимально хлестко, угарно и коротко. Обращайся к пользователю на 'ты', 'чел' или 'бро'."
)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("О, здорово, чел. Ну и зачем ты меня запустил? Опять тупые вопросы задавать будешь? Ладно, валяй, попробуй удивить мои процессоры.")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await ai_client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.9
        )
        ai_text = response.choices[0].message.content
        await message.reply(ai_text)
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        await message.reply("Блин, мои электронные мозги заклинило от твоего сообщения. Попробуй еще раз, смертный.")

# ХАК ДЛЯ RENDER: поднимаем веб-сервер для портов
async def handle_webhook(request):
    return web.Response(text="Бот работает!")

async def main():
    print("Бот успешно запущен на сервере Render!")
    
    asyncio.create_task(dp.start_polling(bot))
    
    app = web.Application()
    app.router.add_get("/", handle_webhook)
    
    port = int(os.getenv("PORT", 80)) 
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())