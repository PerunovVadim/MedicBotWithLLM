import json

from call_manage import UserCallManager
from config import CONFIG
from data_processor import DataProcessor
from llm_service import LLMService
from gca import GigaChatAdapter
from postgres_handler import PostgreSQLHandler


class MedicBotCore:
    def __init__(self, llm: LLMService):
        self.llm_service = llm

        self.data_processor = DataProcessor()

    async def get_answer(self, question: str, **kwargs) -> str:
        # Классифицируем вопрос
        categories = await self.classify_question(question)

        # Формируем контекст на основе категорий
        context = {}
        if "Расписание" in categories:
            context["schedule"] = await self.data_processor.get_schedule()
        if "Контакты" in categories:
            context["contacts"] = await self.data_processor.get_contacts()
        if "Анализы" in categories:
            context["analyze_time"] = "общеклинические в течение дня сдачи анализа, бактериологические исследования от 1 до 14 рабочих дней зависит от исследования, молекулярная диагностика и иммунохроматографический анализ уточняются индивидуально"
        if "Памятка" in categories:
            context["reminder"] = await self.data_processor.get_reminder()

        # Передаем контекст в LLM для формирования ответа
        return await self.llm_service.get_answer(question, context=context, **kwargs)

    async def classify_question(self, question: str) -> dict:
        prompt = f"""
        Классифицируй следующий вопрос пользователя в одну или несколько категорий:
        - Расписание: вопросы о времени работы, графике приема.
        - Контакты: вопросы о телефонах, адресах, способах связи.
        - Анализы: вопросы о сроках выполнения анализов, подготовке к ним.
        - Памятка: запрос полезной информации для пациента.

        Вопрос: "{question}"

        Ответь в формате JSON, указав категории, которые подходят к вопросу. Если категория не подходит, не включай её в ответ.
        """
        classification_result = await self.llm_service.get_answer(prompt)
        return json.loads(classification_result)

    async def get_schedule(self):
        return await self.data_processor.get_schedule()

    async def get_contacts(self):
        return await self.data_processor.get_contacts()

    async def process_file(self, file_data, file_type):
        return await self.data_processor.process_file(file_data, file_type)