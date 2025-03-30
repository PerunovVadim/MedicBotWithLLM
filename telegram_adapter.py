from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from medic_bot import MedicBotCore

def get_persistent_menu():
    return ReplyKeyboardMarkup(
        [
            ["Режим работы"],
            ["Контакты"],
            ["Помощь"],
            ["График приема"]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

class TelegramAdapter():
    def __init__(self, token: str, api_url: str):
        self.token = token
        self.api_url = api_url  # Сохраняем URL API
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Добро пожаловать!", reply_markup=get_persistent_menu())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text

        # Отправляем запрос к API
        try:
            response = requests.post(
                f"{self.api_url}/qa",
                json={"question": user_input},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Проверяем статус ответа
            data = response.json()
            answer = data["answer"]
        except requests.exceptions.RequestException as e:
            answer = "Извините, произошла ошибка при обработке вашего запроса."

        await update.message.reply_text(answer, reply_markup=get_persistent_menu())

    def run(self):
        self.application.run_polling()