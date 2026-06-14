import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Get bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Simple start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Start command received from {update.effective_user.id}")
    await update.message.reply_text(
        "✅ Bot is working!\n\nSend me a video file and I'll give you the file_id."
    )

# Video handler
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id
    print(f"Video received from {update.effective_user.id}")
    await update.message.reply_text(f"file_id: `{file_id}`", parse_mode='Markdown')

# Main function
def main():
    print("Starting bot...")
    print(f"Using token: {BOT_TOKEN[:10]}...")  # Print first 10 chars of token
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Start bot
    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()
