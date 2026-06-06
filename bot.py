import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [8381286547]  # ЗАМЕНИ НА СВОЙ user_id

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DEFAULT_CONTENT = {
    "auto": {"title": "🚗 Страхование авто", "text": "Выберите тип:", "buttons": [["ОСАГО (обязательное)", "osago"], ["КАСКО (добровольное)", "kasko"]]},
    "osago": {"title": "ОСАГО", "text": "Что покрывает ОСАГО..."},
    "kasko": {"title": "КАСКО", "text": "Что покрывает КАСКО..."},
    "home": {"title": "🏠 Страхование дома", "text": "Выберите программу:", "buttons": [["Домовой Эконом", "domovoy_ekonom"], ["Домовой Экспресс", "domovoy_express"], ["Домовой Премиум", "domovoy_premium"]]},
    "domovoy_ekonom": {"title": "Домовой Эконом", "text": "Описание программы..."},
    "domovoy_express": {"title": "Домовой Экспресс", "text": "Описание..."},
    "domovoy_premium": {"title": "Домовой Премиум", "text": "Описание..."},
    "health": {"title": "❤️ Здоровье (ДМС)", "text": "Что входит в ДМС..."},
    "oformit": {"title": "📋 Оформление", "text": "Как оформить полис..."}
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
    builder.button(text="🚗 Авто", callback_data="auto")
    builder.button(text="🏠 Дом", callback_data="home")
    builder.button(text="❤️ Здоровье", callback_data="health")
    builder.button(text="📋 Оформить", callback_data="oformit")
    builder.adjust(2)
    return builder.as_markup()

def get_buttons(section_key):
    data = CONTENT.get(section_key, {})
    builder = InlineKeyboardBuilder()
    for btn in data.get("buttons", []):
        builder.button(text=btn[0], callback_data=btn[1])
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери раздел:", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Команды: /start, /help, /set_auto [текст], /set_health [текст] и т.д. (только для админа)")

@dp.message(Command(commands=["set_auto", "set_health", "set_home", "set_oformit"]))
async def cmd_set(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Только админ.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пример: /set_auto Новый текст 🔥")
        return
    section = parts[0].replace("/set_", "")
    new_text = parts[1].strip()
    if section in CONTENT:
        CONTENT[section]["text"] = new_text
        save_content(CONTENT)
        await message.answer(f"✅ {section} обновлён")
    else:
        await message.answer("Раздел не найден")

@dp.message()
async def any_message(message: types.Message):
    if message.text and message.text.startswith("/"):
        await message.answer("Неизвестная команда. /help")

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    if data in CONTENT:
        text = f"{CONTENT[data]['title']}\n\n{CONTENT[data]['text']}"
        await callback.message.edit_text(text, reply_markup=get_buttons(data) if "buttons" in CONTENT[data] else get_main_menu())
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
