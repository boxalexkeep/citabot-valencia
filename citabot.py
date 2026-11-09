import asyncio
import json
import logging
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_LOGGER = logging.getLogger("citabot")

OPTIONS_FILE = Path("/data/options.json")
OFFICIAL_URL = "https://icp.administracionelectronica.gob.es/icpplus/index.html"

def load_options():
    with OPTIONS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def authorized(update: Update, allowed_chat_id: str) -> bool:
    chat = update.effective_chat
    return bool(chat and str(chat.id) == str(allowed_chat_id))

async def reject(update: Update):
    if update.effective_message:
        await update.effective_message.reply_text(
            "⛔ Цей бот приватний. Ваш Telegram chat ID не має доступу."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed = context.application.bot_data["allowed_chat_id"]
    if not authorized(update, allowed):
        return await reject(update)

    text = (
        "🇪🇸 Вітаю! Це CitaBot Valencia.\n\n"
        "Процедура: TOMA DE HUELLAS (Policía Nacional) — TIE.\n"
        "Зона пошуку: Valencia та найближчі міста провінції.\n\n"
        "Команди:\n"
        "/cita — відкрити офіційний портал запису\n"
        "/check — нагадування, як перевірити запис\n"
        "/help — довідка\n\n"
        "Важливо: бот не бачить закриті слоти й не бронює їх автоматично. "
        "Наявність місць потрібно перевіряти на офіційному порталі; "
        "CAPTCHA та інші захисні перевірки проходьте самостійно."
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Відкрити офіційний запис", url=OFFICIAL_URL)
    ]])
    await update.effective_message.reply_text(text, reply_markup=keyboard)

async def cita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed = context.application.bot_data["allowed_chat_id"]
    if not authorized(update, allowed):
        return await reject(update)

    text = (
        "📅 Офіційний портал Cita Previa:\n"
        f"{OFFICIAL_URL}\n\n"
        "На порталі вибери:\n"
        "1. Provincia: VALENCIA\n"
        "2. Орган/процедура Policía Nacional\n"
        "3. TOMA DE HUELLAS (EXPEDICIÓN DE TARJETA / RENOVACIÓN DE TARJETA, "
        "за назвою, яка відображається для твого випадку)\n\n"
        "Перевіряй також доступні відділення в межах провінції. "
        "Остаточний перелік пунктів і доступність визначає сам портал."
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Перейти до Cita Previa", url=OFFICIAL_URL)
    ]])
    await update.effective_message.reply_text(text, reply_markup=keyboard)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed = context.application.bot_data["allowed_chat_id"]
    if not authorized(update, allowed):
        return await reject(update)
    await update.effective_message.reply_text(
        "🔎 Щоб перевірити наявність вільних записів, відкрий офіційний портал "
        "і пройди перевірку вручну. Ця версія CitaBot не виконує автоматичний "
        "скрейпінг, не обходить CAPTCHA та не підтверджує бронювання.\n\n"
        + OFFICIAL_URL,
        disable_web_page_preview=True,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed = context.application.bot_data["allowed_chat_id"]
    if not authorized(update, allowed):
        return await reject(update)
    await update.effective_message.reply_text(
        "/start — головне меню\n/cita — офіційний портал\n/check — інструкція перевірки"
    )

async def main():
    options = load_options()
    token = str(options.get("telegram_bot_token", "")).strip()
    chat_id = str(options.get("allowed_chat_id", "")).strip()

    if not token or not chat_id:
        raise RuntimeError(
            "Заповніть telegram_bot_token та allowed_chat_id у налаштуваннях CitaBot."
        )

    app = Application.builder().token(token).build()
    app.bot_data["allowed_chat_id"] = chat_id
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cita", cita))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("help", help_command))

    _LOGGER.info("CitaBot Valencia запущено; доступ дозволено лише chat_id=%s", chat_id)
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    try:
        await asyncio.Event().wait()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
