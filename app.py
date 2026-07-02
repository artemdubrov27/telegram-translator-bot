from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ====== Фіктивний сервер для Render ======
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_server).start()

# ====== Основна логіка бота ======
translator = Translator()

LANGUAGES = {
    "Англійська": "en",
    "Литовська": "lt",
    "Українська": "uk",
    "Російська": "ru"
}

MAIN_MENU = [["Почати"], ["Змінити мову"], ["Назад"]]

user_lang = {}
target_lang = {}

def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    update.message.reply_text("Оберіть дію:", reply_markup=reply_markup)

def handle_menu(update: Update, context: CallbackContext):
    choice = update.message.text
    chat_id = update.message.chat_id

    if choice == "Почати":
        keyboard = [[lang] for lang in LANGUAGES.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text("Оберіть мову, з якої перекладати:", reply_markup=reply_markup)

    elif choice == "Змінити мову":
        user_lang.pop(chat_id, None)
        target_lang.pop(chat_id, None)
        update.message.reply_text("🔄 Мови скинуто. Натисніть «Почати», щоб вибрати знову.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))

    elif choice == "Назад":
        update.message.reply_text("↩️ Повернення до головного меню.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))

    elif choice in LANGUAGES:
        set_language(update, context)

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
            src_name = [k for k, v in LANGUAGES.items() if v == user_lang[chat_id]][0]
            dest_name = [k for k, v in LANGUAGES.items() if v == target_lang[chat_id]][0]
            update.message.reply_text(f"✅ Ви обрали переклад з {src_name} на {dest_name}. Надсилайте текст для перекладу.")
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
        src_name = [k for k, v in LANGUAGES.items() if v == src][0]
        dest_name = [k for k, v in LANGUAGES.items() if v == dest][0]
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        update.message.reply_text(
            f"🔤 Переклад ({src_name} → {dest_name}):\n{result.text}",
            reply_markup=reply_markup
        )
    except Exception:
        update.message.reply_text("⚠️ Помилка перекладу. Спробуйте ще раз.")

def main():
    TOKEN = os.getenv("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Команда /start
    dp.add_handler(CommandHandler("start", start))

    # Обробник для кнопок і вибору мов
    dp.add_handler(MessageHandler(
        Filters.text & Filters.regex("^(Почати|Назад|Змінити мову|Англійська|Литовська|Українська|Російська)$"),
        handle_menu
    ))

    # Обробник для тексту, який потрібно перекласти
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, translate_message))

    print("✅ Бот запущений і слухає повідомлення...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
