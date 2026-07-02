from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
import os

translator = Translator()

LANGUAGES = {
    "Англійська": "en",
    "Литовська": "lt",
    "Українська": "uk",
    "Російська": "ru"
}

user_lang = {}
target_lang = {}

def start(update: Update, context: CallbackContext):
    keyboard = [[lang] for lang in LANGUAGES.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("Оберіть мову, з якої перекладати:", reply_markup=reply_markup)

def set_language(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    choice = update.message.text

    if chat_id not in user_lang:
        if choice in LANGUAGES:
            user_lang[chat_id] = LANGUAGES[choice]
            keyboard = [[lang] for lang in LANGUAGES.keys()]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            update.message.reply_text("Тепер оберіть мову, на яку перекладати:", reply_markup=reply_markup)
        else:
            update.message.reply_text("Будь ласка, оберіть мову зі списку.")
    elif chat_id not in target_lang:
        if choice in LANGUAGES:
            target_lang[chat_id] = LANGUAGES[choice]
            update.message.reply_text(f"✅ Ви обрали переклад з {choice}. Надсилайте текст для перекладу.")
        else:
            update.message.reply_text("Будь ласка, оберіть мову зі списку.")
    else:
        translate_message(update, context)

def translate_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id not in user_lang or chat_id not in target_lang:
        update.message.reply_text("Будь ласка, оберіть мови командою /start.")
        return

    src = user_lang[chat_id]
    dest = target_lang[chat_id]
    text = update.message.text

    try:
        result = translator.translate(text, src=src, dest=dest)
        update.message.reply_text(f"🔤 Переклад:\n{result.text}")
    except Exception:
        update.message.reply_text("⚠️ Помилка перекладу. Спробуйте ще раз.")

def main():
    TOKEN = os.getenv("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, set_language))

    print("✅ Бот запущений і слухає повідомлення...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
