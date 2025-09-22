# bot.py
import os
import telebot
from telebot import types
import pypandoc
from PIL import Image
from keep_alive import keep_alive

# Start keep_alive
keep_alive()

# Telegram Bot Token (set as env var for safety)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Supported conversions
text_formats = ["txt", "md", "html", "pdf", "docx"]
image_formats = ["jpg", "jpeg", "png", "webp"]

# Store user’s last uploaded file
user_files = {}

# ========= START COMMAND ==========
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    upload_btn = types.KeyboardButton("📤 Upload File")
    markup.add(upload_btn)
    bot.send_message(message.chat.id,
                     "👋 Hi! আমি File Converter Bot.\n\n📤 প্রথমে একটি ফাইল আপলোড করুন।",
                     reply_markup=markup)

# ========= HANDLE UPLOAD ==========
@bot.message_handler(func=lambda m: m.text == "📤 Upload File")
def ask_file(message):
    bot.send_message(message.chat.id, "🔼 দয়া করে একটি ফাইল পাঠান (ডকুমেন্ট/ইমেজ)।")

@bot.message_handler(content_types=['document', 'photo'])
def handle_file(message):
    try:
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_ext = file_info.file_path.split('.')[-1].lower()
        else:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_ext = "jpg"

        downloaded = bot.download_file(file_info.file_path)
        input_file = f"user_{message.chat.id}.{file_ext}"

        with open(input_file, "wb") as f:
            f.write(downloaded)

        user_files[message.chat.id] = input_file

        # Inline keyboard with format options
        markup = types.InlineKeyboardMarkup()
        if file_ext in text_formats:
            for fmt in text_formats:
                markup.add(types.InlineKeyboardButton(fmt.upper(),
                                                      callback_data=f"convert|{fmt}"))
        elif file_ext in image_formats:
            for fmt in image_formats:
                markup.add(types.InlineKeyboardButton(fmt.upper(),
                                                      callback_data=f"convert|{fmt}"))

        markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back"))

        bot.send_message(message.chat.id,
                         f"✅ ফাইল রিসিভ করা হয়েছে: `{file_ext}`\n\n👉 কনভার্ট করার জন্য নিচে ফরম্যাট সিলেক্ট করুন:",
                         parse_mode="Markdown",
                         reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# ========= HANDLE CONVERSION ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("convert"))
def convert_file(call):
    try:
        chat_id = call.message.chat.id
        if chat_id not in user_files:
            bot.answer_callback_query(call.id, "❌ আগে ফাইল আপলোড করুন।")
            return

        input_file = user_files[chat_id]
        target_format = call.data.split("|")[1]

        output_file = f"output_{chat_id}.{target_format}"

        # Conversion logic
        if input_file.split('.')[-1] in text_formats and target_format in text_formats:
            pypandoc.convert_file(input_file, target_format, outputfile=output_file)
        elif input_file.split('.')[-1] in image_formats and target_format in image_formats:
            img = Image.open(input_file)
            img.save(output_file, target_format.upper())
        else:
            bot.answer_callback_query(call.id, "❌ Unsupported conversion.")
            return

        with open(output_file, "rb") as f:
            bot.send_document(chat_id, f, caption=f"✅ Converted to `{target_format}`",
                              parse_mode="Markdown")

        os.remove(output_file)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Error: {e}")

# ========= BACK BUTTON ==========
@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    upload_btn = types.KeyboardButton("📤 Upload File")
    markup.add(upload_btn)
    bot.send_message(call.message.chat.id,
                     "⬅️ আপনি ফিরে এসেছেন।\n\n📤 এখন নতুন ফাইল আপলোড করতে পারেন।",
                     reply_markup=markup)

# ========= RUN ==========
bot.polling(none_stop=True)
