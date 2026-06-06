import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# Импорт контента из отдельных файлов (редактируй только content_*.py)
from content_auto import AUTO_MAIN, OSAGO, KASKO
from content_health import HEALTH_MAIN, DMS_DETAILS, DMS_PRICES
from content_home import HOME_MAIN, DOMOVOY_EKONOM, DOMOVOY_EXPRESS, DOMOVOY_PREMIUM
from content_oformit import OFORMIT

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚗 Авто", callback_data="auto")
    builder.button(text="🏠 Дом / Квартира", callback_data="home")
    builder.button(text="❤️ Здоровье (ДМС)", callback_data="health")
    builder.button(text="📋 Оформить полис", callback_data="oformit")
    builder.adjust(2)
    return builder.as_markup()

def get_sub_menu(data):
    builder = InlineKeyboardBuilder()
    for text, cb in data.get("buttons", []):
        builder.button(text=text, callback_data=cb)
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот РЕСО-Гарантия.\n\n"
        "Выбери раздел, чтобы узнать условия, тарифы и что покрывает страховка.\n"
        "После — сразу оформи на сайте.",
        reply_markup=get_main_menu()
    )

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data

    if data == "start":
        await callback.message.edit_text(
            "Главное меню. Выбери раздел:",
            reply_markup=get_main_menu()
        )
    elif data == "auto":
        await callback.message.edit_text(
            f"{AUTO_MAIN['title']}\n\n{AUTO_MAIN['text']}",
            reply_markup=get_sub_menu(AUTO_MAIN)
        )
    elif data == "osago":
        await callback.message.edit_text(
            f"{OSAGO['title']}\n\n{OSAGO['text']}",
            reply_markup=get_sub_menu(OSAGO)
        )
    elif data == "kasko":
        await callback.message.edit_text(
            f"{KASKO['title']}\n\n{KASKO['text']}",
            reply_markup=get_sub_menu(KASKO)
        )
    elif data == "home":
        await callback.message.edit_text(
            f"{HOME_MAIN['title']}\n\n{HOME_MAIN['text']}",
            reply_markup=get_sub_menu(HOME_MAIN)
        )
    elif data == "domovoy_ekonom":
        await callback.message.edit_text(
            f"{DOMOVOY_EKONOM['title']}\n\n{DOMOVOY_EKONOM['text']}",
            reply_markup=get_sub_menu(DOMOVOY_EKONOM)
        )
    elif data == "domovoy_express":
        await callback.message.edit_text(
            f"{DOMOVOY_EXPRESS['title']}\n\n{DOMOVOY_EXPRESS['text']}",
            reply_markup=get_sub_menu(DOMOVOY_EXPRESS)
        )
    elif data == "domovoy_premium":
        await callback.message.edit_text(
            f"{DOMOVOY_PREMIUM['title']}\n\n{DOMOVOY_PREMIUM['text']}",
            reply_markup=get_sub_menu(DOMOVOY_PREMIUM)
        )
    elif data == "health":
        await callback.message.edit_text(
            f"{HEALTH_MAIN['title']}\n\n{HEALTH_MAIN['text']}",
            reply_markup=get_sub_menu(HEALTH_MAIN)
        )
    elif data == "dms_details":
        await callback.message.edit_text(
            f"{DMS_DETAILS['title']}\n\n{DMS_DETAILS['text']}",
            reply_markup=get_sub_menu(DMS_DETAILS)
        )
    elif data == "dms_prices":
        await callback.message.edit_text(
            f"{DMS_PRICES['title']}\n\n{DMS_PRICES['text']}",
            reply_markup=get_sub_menu(DMS_PRICES)
        )
    elif data == "oformit":
        await callback.message.edit_text(
            f"{OFORMIT['title']}\n\n{OFORMIT['text']}",
            reply_markup=get_sub_menu(OFORMIT)
        )
    
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
