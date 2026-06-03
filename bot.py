import logging
import os
import asyncio
import edge_tts
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8395312785:AAEYeMxO_fyAH-vux_1h0O2O0BfHRu0JoGU"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

VOICES = {
    "uz": {"name": "🇺🇿 O'zbek (Madina)", "voice": "uz-UZ-MadinaNeural"},
    "uz_m": {"name": "🇺🇿 O'zbek (Sardor)", "voice": "uz-UZ-SardorNeural"},
    "ru": {"name": "🇷🇺 Rus (Svetlana)", "voice": "ru-RU-SvetlanaNeural"},
    "en": {"name": "🇺🇸 Ingliz (Jenny)", "voice": "en-US-JennyNeural"},
    "tr": {"name": "🇹🇷 Turk (Emel)", "voice": "tr-TR-EmelNeural"},
}

user_voice = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Salom {name}! 👋\n\n"
        "Matn yuboring — ovoz bilan qaytaraman!\n\n"
        "/ovoz — til va ovoz tanlash"
    )

async def choose_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(v["name"], callback_data=f"v_{k}")] for k, v in VOICES.items()]
    await update.message.reply_text("🎙 Ovoz tanlang:", reply_markup=InlineKeyboardMarkup(kb))

async def voice_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.replace("v_", "")
    user_voice[q.from_user.id] = key
    await q.edit_message_text(f"✅ {VOICES[key]['name']} tanlandi!\n\nMatn yuboring.")

async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    voice_key = user_voice.get(uid, "uz")
    voice = VOICES[voice_key]["voice"]
    
    msg = await update.message.reply_text("⏳ Ovoz tayyorlanmoqda...")
    try:
        path = f"/tmp/voice_{uid}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)
        
        with open(path, "rb") as f:
            await update.message.reply_voice(voice=f, caption=f"🎙 {VOICES[voice_key]['name']}")
        os.remove(path)
        await msg.delete()
    except Exception as e:
        logging.error(f"TTS xato: {e}")
        await msg.edit_text(f"❌ Xato: {str(e)[:100]}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ovoz", choose_voice))
    app.add_handler(CallbackQueryHandler(voice_cb, pattern="^v_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tts))
    logging.info("Bot ishlamoqda...")
    app.run_polling(drop_pending_updates=True)
