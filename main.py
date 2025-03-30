from config import CONFIG
from telegram_adapter import *

if __name__ == "__main__":



        API_URL = "http://localhost:8000"


        adapter = TelegramAdapter(token=CONFIG["token"], api_url=API_URL)

        # Запускаем бота
        adapter.run()
