import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Start from {update.effective_user.id}")
    await update.message.reply_text(
        "✅ Bot is working!\n\n"
        "Send me a video and I'll give you the file_id.\n\n"
        "*How to send:*\n"
        "• Tap the 📎 (paperclip)\n"
        "• Select 'Video' (not 'File')\n"
        "• Choose your MP4\n\n"
        "Or just send any video file!",
        parse_mode='Markdown'
    )

# Handle video messages
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file_id = video.file_id
    file_size = video.file_size / (1024 * 1024)
    
    print(f"Video received: {file_size:.1f}MB")
    await update.message.reply_text(
        f"✅ *Video Received!*\n\n"
        f"📹 *file_id:*\n`{file_id}`\n\n"
        f"Size: {file_size:.1f}MB",
        parse_mode='Markdown'
    )

# Handle document files that are videos
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith('video/'):
        file_id = doc.file_id
        file_size = doc.file_size / (1024 * 1024)
        
        print(f"Video document received: {file_size:.1f}MB")
        await update.message.reply_text(
            f"✅ *Video File Received!*\n\n"
            f"📹 *file_id:*\n`{file_id}`\n\n"
            f"Size: {file_size:.1f}MB",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("Please send a video file.")

# Handle any other media that might contain video
async def handle_any_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Check for video in different places
    if message.video:
        await handle_video(update, context)
    elif message.document and message.document.mime_type and 'video' in message.document.mime_type:
        await handle_document(update, context)
    elif message.video_note:
        file_id = message.video_note.file_id
        await update.message.reply_text(
            f"✅ *Video Note Received!*\n\nfile_id: `{file_id}`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ No video detected.\n\n"
            "Please send a video file. Make sure to:\n"
            "1. Tap the 📎 attachment icon\n"
            "2. Select 'Video' (not 'File')\n"
            "3. Choose your MP4 file"
        )

def main():
    print("Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # This catches ALL video-related messages
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.Document.VIDEO | filters.VIDEO_NOTE, 
        handle_any_media
    ))
    
    print("Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()
