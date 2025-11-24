import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГУРАЦИЯ ---
# Вставьте сюда токен, который дал @BotFather
TOKEN = "7989479425:AAHR_3nWCYnGdEb66_VgRnd3YnwJY8ojdAs"
# Ваш Telegram ID (можно узнать у @userinfobot)
ADMIN_ID = 123456789

# Конфигурация (сгенерирована автоматически)
CONFIG = {
    "texts": {
        "greeting": "Привет! Это бот Онлайн Сервиса подбора вакансий Работа.РФ.",
        "offer_header": "Вот список всех доступных вакансий в твоем городе. Выбирай и заполняй анкету 👇"
    },
    "offers": {
        "main": [
            { "text": "🚴 Курьер (Самокат)", "url": "https://samokat.ru/vacancy" },
            { "text": "📦 OZON (Озон)", "url": "https://job.ozon.ru/" },
            { "text": "🍔 Повар-кассир / Курьер (Burger King)", "url": "https://burgerking.ru/job" },
            { "text": "🎒 Курьер (Яндекс.Еда / Лавка)", "url": "https://eda.yandex.ru/job" },
            { "text": "📱 Подработка в Яндекс Смена", "url": "https://smena.yandex.ru/" },
            { "text": "🏦 Работа в Т-Банке", "url": "https://www.tbank.ru/career/" },
            { "text": "🛍️ Купер (ex. СберМаркет)", "url": "https://kuper.ru/job" },
            { "text": "💳 Альфа-Банк (Доставка карт)", "url": "https://job.alfabank.ru/" },
            { "text": "🛠️ Сервис «Руки»", "url": "https://hands.ru/job" },
            { "text": "📦 Яндекс.Маркет (Кладовщики)", "url": "https://market.yandex.ru/partners/job" }
        ]
    }
}

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            referral_source TEXT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user: types.User, referral_source: str = None):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, referral_source) VALUES (?, ?, ?, ?)",
            (user.id, user.username, user.full_name, referral_source)
        )
        conn.commit()
    except Exception as e:
        logging.error(f"DB Error: {e}")
    finally:
        conn.close()

def get_stats():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT referral_source, COUNT(*) FROM users GROUP BY referral_source")
    sources = cursor.fetchall()
    conn.close()
    return total, sources

# --- ЛОГИКА БОТА ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    offers = CONFIG['offers'].get('main', [])
    kb = []
    for offer in offers:
        kb.append([InlineKeyboardButton(text=offer['text'], url=offer['url'])])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    args = message.text.split()[1] if len(message.text.split()) > 1 else "organic"
    add_user(message.from_user, args)
    await message.answer(
        CONFIG['texts']['greeting'] + "\n\n" + CONFIG['texts']['offer_header'],
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    total, sources = get_stats()
    stats_msg = f"📊 Статистика:\nВсего пользователей: {total}\n\nИсточники:\n"
    for src, count in sources:
        stats_msg += f"- {src}: {count}\n"
    await message.answer(stats_msg)

async def main():
    init_db()
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
