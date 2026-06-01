import logging
import os
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ===== TOKEN =====
BOT_TOKEN = "8395312785:AAHzqOc1R5Qpsou50leIidTI6Kf0Zu_Ujdk"

# ===== LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===== OVOZLAR =====
VOICES = {
    "uz": {"name": "🇺🇿 O'zbek", "lang": "uz", "tld": "com"},
    "ru": {"name": "🇷🇺 Rus",    "lang": "ru", "tld": "com"},
    "en": {"name": "🇺🇸 Ingliz", "lang": "en", "tld": "com"},
    "tr": {"name": "🇹🇷 Turk",   "lang": "tr", "tld": "com"},
}

# Foydalanuvchilarning tanlagan ovozi
user_voice = {}

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Salom, {user}! 👋\n\n"
        "Men matnni ovozga aylantirib beraman.\n\n"
        "📝 Faqat matn yuboring — men uni o'qib beraman!\n\n"
        "⚙️ Ovoz tanlash: /ovoz\n"
        "ℹ️ Yordam: /help"
    )

# ===== /help =====
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Buyruqlar:</b>\n\n"
        "• Matn yuboring → ovoz qaytaradi\n"
        "• /ovoz — ovoz tilini tanlash\n"
        "• /start — boshidan boshlash\n\n"
        "💡 <b>Maslahat:</b> Uzoq matnlarni ham yuboravering!",
        parse_mode="HTML"
    )

# ===== /ovoz — til tanlash =====
async def choose_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, val in VOICES.items():
        keyboard.append([InlineKeyboardButton(val["name"], callback_data=f"voice_{key}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎙 Ovoz tilini tanlang:", reply_markup=reply_markup)

# ===== Callback: ovoz tanlanganda =====
async def voice_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_key = query.data.replace("voice_", "")
    user_id = query.from_user.id
    user_voice[user_id] = lang_key
    voice_name = VOICES[lang_key]["name"]
    await query.edit_message_text(f"✅ Ovoz tanlandi: {voice_name}\n\nEndi matn yuboring!")

# ===== Matn kelganda — ovozga aylantir =====
async def text_to_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Default: o'zbek
    lang_key = user_voice.get(user_id, "uz")
    voice = VOICES[lang_key]

    await update.message.reply_text("⏳ Ovoz tayyorlanmoqda...")

    try:
        # gTTS bilan ovoz yaratish
        tts = gTTS(text=text, lang=voice["lang"], tld=voice["tld"], slow=False)
        file_path = f"voice_{user_id}.mp3"
        tts.save(file_path)

        # Ovozni yuborish
        with open(file_path, "rb") as audio:
            await update.message.reply_voice(
                voice=audio,
                caption=f"🎙 {voice['name']} ovozida"
            )

        # Faylni o'chirish
        os.remove(file_path)

    except Exception as e:
        logging.error(f"Xato: {e}")
        await update.message.reply_text(
            "❌ Xato yuz berdi. Iltimos qaytadan urinib ko'ring.\n"
            "Matn juda uzun bo'lsa, qisqartib yuboring."
        )

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ovoz", choose_voice))
    app.add_handler(CallbackQueryHandler(voice_selected, pattern="^voice_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_voice))

    print("✅ Bot ishlamoqda... (Ctrl+C bilan to'xtatish)")
    app.run_polling()

if __name__ == "__main__":
    main()
