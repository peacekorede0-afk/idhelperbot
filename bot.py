import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working! Send me a video file.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id
    await update.message.reply_text(f"file_id: {file_id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
