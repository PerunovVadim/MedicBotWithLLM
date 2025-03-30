from telegram import Update, ReplyKeyboardMarkup
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes


def get_persistent_menu():
    """
    Создает и возвращает постоянное меню с кнопками для Telegram-бота.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками, которые отображаются пользователю.
    """
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


class TelegramAdapter():
    """
    Класс TelegramAdapter представляет собой адаптер для взаимодействия Telegram-бота с внешним API.
    Он обрабатывает команды и сообщения от пользователей, отправляет запросы к API и возвращает ответы.

    Attributes:
        token (str): Токен Telegram-бота, используемый для авторизации.
        api_url (str): URL внешнего API, к которому отправляются запросы.
        application: Экземпляр приложения Telegram для обработки событий.
    """

    def __init__(self, token: str, api_url: str):
        """
        Инициализирует экземпляр класса TelegramAdapter.

        Args:
            token (str): Токен Telegram-бота.
            api_url (str): URL внешнего API.
        """
        self.token = token
        self.api_url = api_url  # Сохраняем URL API
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """
        Настройка обработчиков команд и сообщений для Telegram-бота.
        Добавляет обработчики для команды /start и текстовых сообщений.
        """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start. Отправляет приветственное сообщение и отображает постоянное меню.

        Args:
            update (Update): Объект, содержащий информацию о входящем обновлении (сообщении).
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения обработчика.
        """
        await update.message.reply_text("Добро пожаловать!", reply_markup=get_persistent_menu())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик текстовых сообщений от пользователей. Отправляет запрос к внешнему API
        с текстом сообщения и возвращает ответ пользователю.

        Args:
            update (Update): Объект, содержащий информацию о входящем обновлении (сообщении).
            context (ContextTypes.DEFAULT_TYPE): Контекст выполнения обработчика.
        """
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
        """
        Запускает бота в режиме опроса (polling).
        Бот начинает получать обновления от Telegram и обрабатывать их.
        """
        self.application.run_polling()