import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from youtube_dl import YoutubeDL
import ffmpeg

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = '7743242157:AAFpsWcGEnAFhT3YFUflBiN9Gk8LEP2s-KE'

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a YouTube link to play music in the voice chat.')

# Command to play music
def play(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    url = update.message.text

    # Download the audio from YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.mp3',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Convert the audio to the required format
    stream = ffmpeg.input('audio.mp3')
    stream = ffmpeg.output(stream, 'audio.ogg', acodec='libopus')
    ffmpeg.run(stream)

    # Send the audio to the voice chat
    context.bot.send_voice(chat_id=chat_id, voice=open('audio.ogg', 'rb'))

    # Clean up
    os.remove('audio.mp3')
    os.remove('audio.ogg')

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, play))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()