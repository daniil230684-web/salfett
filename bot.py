import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import ClientSession

# Берем ключи из настроек Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

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
    await message.answer("О, здорово, чел. Ну и зачем ты меня запустил? Опять тупые вопросы задавать будешь? Ладно, валяй, попробуй удивить мои процессоры.")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com", 
        "X-Title": "Neuroham Bot"
    }
    data = {
        "model": "deepseek/deepseek-chat:free",
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
                    print(f"ОТВЕТ ОТ OPENROUTER (Статус {status}): {result}")
                    await message.reply("Блин, мои электронные мозги заклинило от твоего сообщения. Попробуй еще раз, смертный.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        await message.reply("Блин, мои электронные мозги заклинило от твоего сообщения. Попробуй еще раз, смертный.")

async def main():
    print("Бот успешно запущен в режиме прямого опроса (Polling)!")
    # Перед стартом принудительно удаляем любые вебхуки, если они зависли в ТГ
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())