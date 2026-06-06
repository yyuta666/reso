import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# Токен бота (получи у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==================== КОНТЕНТ БОТА (ЛЕГКО МЕНЯТЬ) ====================
# ЗАМЕНИ ТЕКСТЫ НИЖЕ НА РЕАЛЬНЫЕ ДАННЫЕ ОТ РЕСО-ГАРАНТИЯ

CONTENT = {
    "auto": {
        "title": "🚗 Страхование авто",
        "text": "Выберите тип:",
        "buttons": [
            ("ОСАГО (обязательное)", "osago"),
            ("КАСКО (добровольное)", "kasko")
        ]
    },
    "osago": {
        "title": "ОСАГО — Обязательное автострахование",
        "text": """Что покрывает:
• Вред жизни и здоровью третьих лиц — до 500 000 ₽
• Вред имуществу третьих лиц — до 400 000 ₽

Примерная стоимость: рассчитывается индивидуально (от ~5 000 ₽/год для аккуратных водителей).

Условия: Полис оформляется онлайн за 5 минут. Нужны данные авто и водителей.

Что дальше: Перейдите на сайт для расчёта и оформления.""",
        "buttons": [("Назад к авто", "auto"), ("Оформить", "oformit")]
    },
    "kasko": {
        "title": "КАСКО — Добровольное автострахование",
        "text": """Что покрывает:
• Ущерб от ДТП, угона, пожара, стихии, третьих лиц
• Ремонт или выплата

Примерная стоимость (2026):
• Для авто ~1,3 млн ₽ — от 9 600 ₽/год (Каско-Профи Лайт)
• Полное КАСКО — 3-10% от стоимости авто

Программы: Каско-Профи, Каско-Профи Лайт, РЕСОавто-GAP.

Условия: Без учёта износа в некоторых программах. Ремонт у официалов.""",
        "buttons": [("Назад к авто", "auto"), ("Оформить", "oformit")]
    },
    "home": {
        "title": "🏠 Страхование дома / квартиры",
        "text": "Выберите программу:",
        "buttons": [
            ("Домовой Эконом", "domovoy_ekonom"),
            ("Домовой Экспресс", "domovoy_express"),
            ("Домовой Премиум", "domovoy_premium")
        ]
    },
    "domovoy_ekonom": {
        "title": "Домовой. Эконом — от 8 000 ₽/год",
        "text": """Что покрывает:
• Пожар, залив, стихия, кража со взломом
• Ответственность перед соседями

Страховые суммы (пример):
• Конструкция: 3,5 млн ₽
• Отделка: 600 тыс. ₽
• Движимое имущество: 400 тыс. ₽
• Ответственность: 400 тыс. ₽

Условия: Оформление онлайн без осмотра. Выплата без справок в расширенных программах.""",
        "buttons": [("Назад к дому", "home"), ("Оформить", "oformit")]
    },
    "domovoy_express": {
        "title": "Домовой. Экспресс — от 9 500 ₽/год",
        "text": """Что покрывает: то же + больше лимитов

Страховые суммы (пример):
• Конструкция: 6 млн ₽
• Отделка: 650 тыс. ₽
• Движимое имущество: 550 тыс. ₽
• Ответственность: 650 тыс. ₽

Дополнительно можно добавить: падение БПЛА, терроризм, сервис (сантехник и т.д.).""",
        "buttons": [("Назад к дому", "home"), ("Оформить", "oformit")]
    },
    "domovoy_premium": {
        "title": "Домовой. Премиум — от 18 700 ₽/год",
        "text": """Максимальная защита:
• Конструкция: 10 млн ₽
• Отделка: 1,7 млн ₽
• Движимое имущество: 1,1 млн ₽
• Ответственность: 1,1 млн ₽

Всё включено: падение БПЛА, терроризм, без износа, без справок.""",
        "buttons": [("Назад к дому", "home"), ("Оформить", "oformit")]
    },
    "health": {
        "title": "❤️ Страхование здоровья (ДМС)",
        "text": """Основные программы ДМС РЕСО-Гарантия:

Что входит в базовую:
• Приёмы врачей и диагностика
• Вызов врача на дом
• Скорая медицинская помощь
• Телемедицина (видеоконсультации)

Дополнительно можно добавить:
• Стоматология
• Экстренный стационар
• Онкоподдержка

Примерная стоимость: от нескольких тысяч рублей в год (зависит от возраста, региона и программы).

Точная цена — на сайте после заполнения анкеты.""",
        "buttons": [("Подробнее на сайте", "health_site"), ("Оформить", "oformit")]
    },
    "oformit": {
        "title": "📋 Оформление полиса",
        "text": """Чтобы оформить полис РЕСО-Гарантия:

1. Перейдите на официальный сайт: https://reso.ru/
2. Выберите нужный раздел (Авто / Дом / Здоровье)
3. Заполните данные онлайн
4. Оплатите и получите полис на email

Всё можно сделать за 5-15 минут без визита в офис.

Нужна помощь с выбором? Напишите сюда — подскажу по публичным данным.""",
        "buttons": [("Главное меню", "start")]
    }
}

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚗 Авто", callback_data="auto")
    builder.button(text="🏠 Дом / Квартира", callback_data="home")
    builder.button(text="❤️ Здоровье (ДМС)", callback_data="health")
    builder.button(text="📋 Оформить полис", callback_data="oformit")
    builder.adjust(2)
    return builder.as_markup()

def get_sub_menu(section):
    data = CONTENT.get(section, {})
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
    elif data in ["auto", "home", "health"]:
        section = CONTENT[data]
        await callback.message.edit_text(
            f"{section['title']}\n\n{section['text']}",
            reply_markup=get_sub_menu(data)
        )
    elif data in ["osago", "kasko", "domovoy_ekonom", "domovoy_express", "domovoy_premium"]:
        section = CONTENT[data]
        await callback.message.edit_text(
            f"{section['title']}\n\n{section['text']}",
            reply_markup=get_sub_menu(data)
        )
    elif data == "oformit":
        section = CONTENT["oformit"]
        await callback.message.edit_text(
            f"{section['title']}\n\n{section['text']}",
            reply_markup=get_sub_menu("oformit")
        )
    elif data == "health_site":
        await callback.message.edit_text(
            "Подробная информация о ДМС:\nhttps://reso.ru/individual/medicine/",
            reply_markup=get_sub_menu("health")
        )
    
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
