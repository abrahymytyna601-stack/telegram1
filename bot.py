import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

flask_app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_info = None
    caption = ""

    if update.message.document:
        file = update.message.document
        caption = file.file_name
        file_info = file
    elif update.message.photo:
        file = update.message.photo[-1]
        caption = "Photo"
    elif update.message.audio:
        file_info = update.message.audio
        caption = file_info.title or "Audio"
    elif update.message.video:
        file_info = update.message.video
        caption = file_info.file_name or "Video"
    elif update.message.voice:
        file_info = update.message.voice
        caption = "Voice message"

    if file_info:
        await update.message.reply_text(
            f"✅ فایل دریافت شد:\n"
            f"📄 نام: {caption}\n"
            f"🆔 File ID: `{file_info.file_id}`\n"
            f"📦 حجم: {file_info.file_size / 1024:.2f} KB",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ این نوع فایل پشتیبانی نمی‌شود.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فایل بفرست تا اطلاعاتشو بدم 😊")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_file))

@flask_app.route("/", methods=["GET"])
def home():
    return "ربات تلگرام فعاله ✅"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return "OK"

if __name__ == "__main__":
    import asyncio
    from threading import Thread

    def run_flask():
        flask_app.run(host="0.0.0.0", port=8080)

    Thread(target=run_flask).start()

    asyncio.run(bot_app.initialize())
    asyncio.run(bot_app.start())
