import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [8381286547] GREETING = "Привет! Выбери раздел:"


logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Полный список разделов
SECTIONS = [
    "auto", "property", "life_health", "dms", 
    "travel", "ipoteka", "liability", "business"
]

DEFAULT_CONTENT = {
    "auto": {
        "title": "🚗 Автострахование",
        "text": "ОСАГО и КАСКО от РЕСО-Гарантия.\n\nВыберите тип:",
        "buttons": [["ОСАГО", "osago"], ["КАСКО", "kasko"]]
    },
    "property": {
        "title": "🏠 Имущество",
        "text": "Страхование квартиры, дома, дачи и ответственности перед соседями."
    },
    "life_health": {
        "title": "❤️ Жизнь и здоровье",
        "text": "Страхование жизни и от несчастных случаев."
    },
    "dms": {
        "title": "🏥 Добровольное медицинское страхование",
        "text": "ДМС — медицинская помощь, врачи, скорая, телемедицина."
    },
    "travel": {
        "title": "✈️ Путешествия",
        "text": "Страхование выезда за границу и поездок по России."
    },
    "ipoteka": {
        "title": "🏦 Ипотека",
        "text": "Ипотечное страхование недвижимости."
    },
    "liability": {
        "title": "⚖️ Ответственность",
        "text": "Страхование гражданской и профессиональной ответственности."
    },
    "business": {
        "title": "🏢 Страхование бизнеса",
        "text": "Страхование для юридических лиц и предпринимателей."
    }
}

def load_content():
    if not os.path.exists("content.json"):
        with open("content.json", "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONTENT, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONTENT.copy()
    with open("content.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_content(data):
    with open("content.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CONTENT = load_content()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Оформить полис" — первой и на всю ширину
    builder.button(text="📋 Оформить полис", callback_data="oformit")
    
    # Остальные разделы
    builder.button(text="🚗 Автострахование", callback_data="auto")
    builder.button(text="🏠 Имущество", callback_data="property")
    builder.button(text="❤️ Жизнь и здоровье", callback_data="life_health")
    builder.button(text="🏥 ДМС", callback_data="dms")
    builder.button(text="✈️ Путешествия", callback_data="travel")
    builder.button(text="🏦 Ипотека", callback_data="ipoteka")
    builder.button(text="⚖️ Ответственность", callback_data="liability")
    builder.button(text="🏢 Страхование бизнеса", callback_data="business")
    
    builder.adjust(1, 2)   # первая кнопка на всю ширину, остальные по 2 в ряд
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(GREETING, reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = "Доступные команды:\n/start — главное меню\n/help — эта справка\n"
    for sec in SECTIONS:
        text += f"/set_{sec} [текст] — изменить раздел (только админ)\n"
    await message.answer(text)

@dp.message(Command(commands=[f"set_{sec}" for sec in SECTIONS]))
async def cmd_set(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Только админ может редактировать.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пример: /set_auto Новый текст здесь 🔥")
        return

    command = parts[0]
    new_text = parts[1].strip()
    section = command.replace("/set_", "")

    if section in CONTENT:
        CONTENT[section]["text"] = new_text
        save_content(CONTENT)
        await message.answer(f"✅ Раздел {section} обновлён!")
    else:
        await message.answer("Раздел не найден.")

@dp.message()
async def any_message(message: types.Message):
    if message.text and message.text.startswith("/"):
        await message.answer("Неизвестная команда. Напиши /help")

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    if data in CONTENT:
        section = CONTENT[data]
        text = f"{section['title']}\n\n{section.get('text', '')}"
        builder = InlineKeyboardBuilder()
        for btn in section.get("buttons", []):
            builder.button(text=btn[0], callback_data=btn[1])
        builder.adjust(1)
        await callback.message.edit_text(text, reply_markup=builder.as_markup() if section.get("buttons") else get_main_menu())
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
