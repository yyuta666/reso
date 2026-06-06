import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [8381286547]   # ← ЗАМЕНИ НА СВОЙ user_id (узнать у @userinfobot)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def load_content():
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
    await message.answer(
        "Команды:\n"
        "/start — меню\n"
        "/set_auto [текст] — изменить Авто (только админ)\n"
        "/set_health [текст] — изменить Здоровье\n"
        "/set_home [текст] — изменить Дом\n"
        "/set_oformit [текст] — изменить Оформление\n\n"
        "Пример: /set_auto 🔥 Новый текст здесь"
    )

@dp.message(Command(commands=["set_auto", "set_health", "set_home", "set_oformit"]))
async def cmd_set(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Только админ может менять текст.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("После команды напиши новый текст.\nПример: /set_auto Новый текст 🔥")
        return

    command = parts[0]
    new_text = parts[1].strip()
    section = command.replace("/set_", "")

    if section in CONTENT:
        CONTENT[section]["text"] = new_text
        save_content(CONTENT)
        await message.answer(f"✅ Раздел {section} обновлён!")
    else:
        await message.answer("Такой раздел не найден.")

@dp.message()
async def any_message(message: types.Message):
    if message.text and message.text.startswith("/"):
        await message.answer("Неизвестная команда. Напиши /help")

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    if data in ["auto", "home", "health", "oformit"]:
        await callback.message.edit_text(
            f"{CONTENT[data]['title']}\n\n{CONTENT[data]['text']}",
            reply_markup=get_buttons(data)
        )
    else:
        content = CONTENT.get(data)
        if content:
            await callback.message.edit_text(
                f"{content['title']}\n\n{content['text']}",
                reply_markup=get_main_menu()
            )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
