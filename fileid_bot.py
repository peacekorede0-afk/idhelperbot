import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    await update.message.reply_text(
        "🎥 *Video File ID Generator*\n\n"
        "Simply send me any video and I'll give you its file_id.\n\n"
        "*How to use:*\n"
        "1. Send me a video\n"
        "2. Copy the file_id from my reply\n"
        "3. Use it in your main bot\n\n"
        "Made for BitAl Bot Setup",
        parse_mode='Markdown'
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video messages and return the file_id."""
    video = update.message.video
    file_id = video.file_id
    
    response = (
        f"✅ *Video Received!*\n\n"
        f"📹 *file_id:*\n"
        f"`{file_id}`\n\n"
        f"---\n"
        f"*Copy this file_id and paste it into your main bot's code.*"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')
    print(f"✅ Sent file_id for video")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video files sent as documents."""
    document = update.message.document
    if document.mime_type and document.mime_type.startswith('video/'):
        file_id = document.file_id
        
        response = (
            f"✅ *Video Document Received!*\n\n"
            f"📹 *file_id:*\n"
            f"`{file_id}`\n\n"
            f"---\n"
            f"*Copy this file_id and paste it into your main bot's code.*"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        print(f"✅ Sent file_id for video document")
    else:
        await update.message.reply_text("📄 Not a video file.")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Start bot
    print("🤖 File ID Bot is running...")
    print("Send videos to get their file_id")
    application.run_polling()

if __name__ == '__main__':
    main()
