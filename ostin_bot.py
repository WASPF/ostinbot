import asyncio
import re
import urllib.parse
import streamlit as st
from aiogram import Bot, Dispatcher, types, F

# --- БЕЗОПАСНАЯ КОНФИГУРАЦИЯ ---
# Теперь ключ берется из скрытых настроек Streamlit
TOKEN = st.secrets.get("OSINT_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_links(q_type, val):
    enc = urllib.parse.quote(val)
    links = []
    
    if q_type == "email":
        links = [
            ("📧 Проверка соцсетей (EPIOS)", f"https://epios.com/?email={enc}"),
            ("🔐 Утечки паролей (HIBP)", f"https://haveibeenpwned.com/account/{enc}"),
            ("🔎 Поиск в базах данных (IntelX)", f"https://intelx.io/?s={enc}")
        ]
    elif q_type == "nickname":
        links = [
            ("👤 Поиск по 150+ сайтам (SocialSearcher)", f"https://www.social-searcher.com/search-users/?q={enc}"),
            ("🐦 Поиск в Twitter (X)", f"https://twitter.com/search?q={enc}&f=user"),
            ("💬 Поиск в Telegram чатах (Lyzem)", f"https://lyzem.com/search?q={enc}")
        ]
    elif q_type == "phone":
        clean_p = re.sub(r'\D', '', val)
        links = [
            ("📞 Кто звонил? (Sync.me)", f"https://sync.me/search/?number={clean_p}"),
            ("📱 Проверка (TrueCaller)", f"https://www.truecaller.com/search/global/{clean_p}"),
            ("🤖 Глаз Бога (UA)", f"https://t.me/OpenDataUABot?start={clean_p}")
        ]
    elif q_type == "crypto":
        links = [
            ("💰 Транзакции BTC/ETH", f"https://www.blockchain.com/explorer/search?search={enc}"),
            ("🕵️ Анализ кошелька (Arkham)", f"https://platform.arkhamintelligence.com/explorer/search/{enc}")
        ]
    elif q_type == "car":
        links = [
            ("🚗 История авто (UA)", f"https://baza-gai.com.ua/nomer/{enc}"),
            ("📸 Фото авто на дорогах", f"https://platesmania.com/ua/search?nomer={enc}")
        ]
        
    return links

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "🕵️‍♂️ **OSINT Менеджер v2.1 (Security Edition)**\n\n"
        "Отправь мне данные для поиска:\n"
        "• **Ник** (ivan_crypto)\n"
        "• **Email** (test@mail.com)\n"
        "• **Телефон** (+380...)\n"
        "• **Крипто-кошелек** (0x...)\n"
        "• **Госномер авто** (AA1111AA)\n\n"
        "Я сформирую безопасные ссылки для разведки!",
        parse_mode="Markdown"
    )

@dp.message()
async def investigate(message: types.Message):
    text = message.text.strip()
    
    # Авто-определение типа данных
    if re.match(r"[^@]+@[^@]+\.[^@]+", text):
        t, label = "email", "📧 Почта"
    elif re.match(r"^\+?[\d\s\-]{10,}$", text):
        t, label = "phone", "📞 Телефон"
    elif re.match(r"^(0x|[13b][a-km-zA-HJ-NP-Z1-9]{25,39})", text):
        t, label = "crypto", "💰 Крипто-адрес"
    elif re.match(r"^[A-Z]{2}\d{4}[A-Z]{2}$", text.upper()):
        t, label = "car", "🚗 Госномер"
        text = text.upper()
    else:
        t, label = "nickname", "👤 Ник"

    links = get_links(t, text)
    kb = [[types.InlineKeyboardButton(text=n, url=u)] for n, u in links]
    
    await message.answer(
        f"🔎 **Разведка по {label}:** `{text}`",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )

async def main():
    st.title("🕵️‍♂️ OSINT Backend")
    st.write("Бот запущен и работает через безопасные Secrets.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())