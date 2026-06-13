import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.environ.get("PORT", 8080))

# Flask app for Railway health checks
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

# Create downloads directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 *YouTube to File ID Bot*\n\n"
        "Send me a YouTube link and I'll:\n"
        "1. Download the video\n"
        "2. Send it to you\n"
        "3. Give you the file_id\n\n"
        "*⚠️ Note:* Videos over 20MB will fail due to Telegram's limit.\n\n"
        "Or just send me an MP4 file directly!",
        parse_mode='Markdown'
    )

async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if 'youtu' not in url:
        return
    
    await update.message.reply_text("📥 Downloading video from YouTube... This may take a minute.")
    
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = filename.replace('.webm', '.mp4')
        
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        if file_size > 20:
            await update.message.reply_text(
                f"⚠️ Video is {file_size:.1f}MB, exceeds Telegram's 20MB limit.\n\n"
                f"Download manually: {url}"
            )
            os.remove(filename)
            return
        
        with open(filename, 'rb') as video_file:
            message = await update.message.reply_video(video=video_file)
            file_id = message.video.file_id
        
        os.remove(filename)
        
        await update.message.reply_text(
            f"✅ *Success!*\n\n"
            f"📹 *file_id:*\n"
            f"`{file_id}`\n\n"
            f"File size: {file_size:.1f}MB\n\n"
            f"*Copy this file_id for your main bot.*",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_video_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file_id = video.file_id
    file_size = video.file_size / (1024 * 1024)
    
    await update.message.reply_text(
        f"✅ *Video Received!*\n\n"
        f"📹 *file_id:*\n"
        f"`{file_id}`\n\n"
        f"File size: {file_size:.1f}MB\n\n"
        f"*Copy this for your main bot*",
        parse_mode='Markdown'
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith('video/'):
        await update.message.reply_text(
            f"✅ *Video Document Received!*\n\n"
            f"📹 *file_id:*\n"
            f"`{doc.file_id}`",
            parse_mode='Markdown'
        )

def main():
    # Start Flask server for Railway
    Thread(target=run_flask, daemon=True).start()
    
    # Create bot application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_file))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Clear any existing webhook
    async def clear_and_start():
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Cleared old webhook state")
        print("🤖 Bot starting...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
    
    asyncio.run(clear_and_start())
    
    print(f"🚀 Bot running on port {PORT}")
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
