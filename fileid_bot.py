import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.environ.get("PORT", 8080))

# Flask app for Railway
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 *Video File ID Generator*\n\n"
        "*How to use:*\n"
        "1. Send me a video file (MP4)\n"
        "2. I will reply with the file_id\n"
        "3. Copy that ID for your main bot\n\n"
        "*Note:* Send the actual video file, not a YouTube link!",
        parse_mode='Markdown'
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file_id = video.file_id
    
    response = (
        f"✅ *Video Received!*\n\n"
        f"📹 *file_id:*\n"
        f"`{file_id}`\n\n"
        f"*Copy this entire file_id* and paste it into your main bot's code."
    )
    await update.message.reply_text(response, parse_mode='Markdown')
    print(f"Sent file_id to user {update.effective_user.id}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith('video/'):
        response = (
            f"✅ *Video Document Received!*\n\n"
            f"📹 *file_id:*\n"
            f"`{doc.file_id}`\n\n"
            f"*Copy this file_id for your main bot*"
        )
        await update.message.reply_text(response, parse_mode='Markdown')

def main():
    # Start Flask thread
    Thread(target=run_flask, daemon=True).start()
    
    # Create bot application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Clear any existing webhook
    async def start_bot():
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Cleared old webhook")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print(f"🤖 Bot is running! Send videos to get file_ids")
    
    asyncio.run(start_bot())
    
    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Bot stopped")

if __name__ == '__main__':
    main()
