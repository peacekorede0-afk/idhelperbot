import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Create temp directory for downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 *YouTube to File ID Bot*\n\n"
        "Send me a YouTube link and I'll:\n"
        "1. Download the video\n"
        "2. Send it to you\n"
        "3. Give you the file_id\n\n"
        "*⚠️ Note:* Videos over 20MB will fail due to Telegram's limit.",
        parse_mode='Markdown'
    )

async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # Check if it's a YouTube URL
    if 'youtu' not in url:
        return
    
    await update.message.reply_text("📥 Downloading video from YouTube... This may take a minute.")
    
    try:
        # Download video using yt-dlp
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
        
        # Check file size
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        if file_size > 20:
            await update.message.reply_text(
                f"⚠️ Video is {file_size:.1f}MB, which exceeds Telegram's 20MB limit.\n\n"
                f"You'll need to download it manually: {url}"
            )
            os.remove(filename)
            return
        
        # Send video to get file_id
        with open(filename, 'rb') as video_file:
            message = await update.message.reply_video(video=video_file)
            file_id = message.video.file_id
        
        # Clean up
        os.remove(filename)
        
        # Send the file_id
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
    """Handle video files sent directly - gives file_id instantly"""
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

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_file))
    
    print("🤖 Bot running - accepts YouTube links and video files!")
    app.run_polling()

if __name__ == '__main__':
    main()
