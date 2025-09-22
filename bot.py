# bot.py
import os
import telebot
import pypandoc
from PIL import Image
from keep_alive import keep_alive

# Start keep_alive
keep_alive()

# Telegram Bot Token (set as env var for safety)
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set this in Render/Heroku
bot = telebot.TeleBot(BOT_TOKEN)

# Supported conversions
text_formats = ["txt", "md", "html", "pdf", "docx"]
image_formats = ["jpg", "jpeg", "png", "webp"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hi 👋 Send me a file and I’ll convert it for you!\n\n"
                          "Text: txt ↔ pdf ↔ docx\n"
                          "Images: jpg ↔ png ↔ webp")

@bot.message_handler(content_types=['document', 'photo'])
def handle_file(message):
    try:
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_ext = file_info.file_path.split('.')[-1].lower()
        else:
            # Photo case (Telegram sends compressed images as jpg)
            file_info = bot.get_file(message.photo[-1].file_id)
            file_ext = "jpg"

        downloaded = bot.download_file(file_info.file_path)
        input_file = f"input.{file_ext}"

        with open(input_file, "wb") as f:
            f.write(downloaded)

        # Conversion logic
        if file_ext in text_formats:
            output_file = "output.pdf"
            pypandoc.convert_file(input_file, "pdf", outputfile=output_file)
        elif file_ext in image_formats:
            img = Image.open(input_file)
            output_file = "output.png" if file_ext != "png" else "output.jpg"
            img.save(output_file)
        else:
            bot.reply_to(message, "❌ Unsupported file format.")
            return

        # Send file back
        with open(output_file, "rb") as f:
            bot.send_document(message.chat.id, f)

        os.remove(input_file)
        os.remove(output_file)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# Run polling
bot.polling(none_stop=True)
          
