import json

from data_processor import DataProcessor
from llm_service import LLMService


class MedicBotCore:
    """
    Класс MedicBotCore представляет собой ядро медицинского бота, который обрабатывает вопросы пользователей,
    классифицирует их и формирует ответы с использованием данных из различных источников.

    Attributes:
        llm_service (LLMService): Сервис для работы с языковой моделью (LLM), который используется для генерации ответов.
        data_processor (DataProcessor): Обработчик данных, который предоставляет информацию с веб-сайтов и файлов.
    """

    def __init__(self, llm: LLMService):
        """
        Инициализирует экземпляр класса MedicBotCore.

        Args:
            llm (LLMService): Экземпляр сервиса языковой модели (LLM).
        """
        self.llm_service = llm
        self.data_processor = DataProcessor()

    async def get_answer(self, question: str, **kwargs) -> str:
        """
        Асинхронно обрабатывает вопрос пользователя, классифицирует его и формирует ответ на основе контекста.

        Args:
            question (str): Вопрос пользователя.
            **kwargs: Дополнительные параметры для передачи в LLMService.

        Returns:
            str: Текстовый ответ на вопрос пользователя.

        Описание логики:
        - Классифицирует вопрос с помощью метода `classify_question`.
        - Формирует контекст на основе категорий вопроса, используя данные из `DataProcessor`.
        - Передает контекст и вопрос в LLM для генерации ответа.
        """
        # Классифицируем вопрос
        categories = await self.classify_question(question)

        # Формируем контекст на основе категорий
        context = {}
        if "Расписание" in categories:
            context["schedule"] = await self.data_processor.get_schedule()
        if "Контакты" in categories:
            context["contacts"] = await self.data_processor.get_contacts()
        if "Анализы" in categories:
            context["analyze_time"] = (
                "общеклинические в течение дня сдачи анализа, "
                "бактериологические исследования от 1 до 14 рабочих дней зависит от исследования, "
                "молекулярная диагностика и иммунохроматографический анализ уточняются индивидуально"
            )
        if "Памятка" in categories:
            context["reminder"] = await self.data_processor.get_reminder()

        # Передаем контекст в LLM для формирования ответа
        return await self.llm_service.get_answer(question, context=context, **kwargs)

    async def classify_question(self, question: str) -> dict:
        """
        Асинхронно классифицирует вопрос пользователя в одну или несколько категорий.

        Args:
            question (str): Вопрос пользователя.

        Returns:
            dict: Словарь с категориями, к которым относится вопрос.

        Описание логики:
        - Формируется промпт для языковой модели, содержащий описание категорий.
        - Промпт отправляется в LLM, которая возвращает JSON с подходящими категориями.
        - Результат парсится и возвращается в виде словаря.
        """
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
        """
        Асинхронно получает расписание с веб-сайта.

        Returns:
            str: Текстовое представление расписания.
        """
        return await self.data_processor.get_schedule()

    async def get_contacts(self):
        """
        Асинхронно получает контактную информацию с веб-сайта.

        Returns:
            str: Текстовое представление контактной информации.
        """
        return await self.data_processor.get_contacts()

    async def process_file(self, file_data, file_type):
        """
        Асинхронно обрабатывает файлы различных типов (PDF, Excel, изображения).

        Args:
            file_data: Двоичные данные файла.
            file_type (str): Тип файла (например, 'pdf', 'xlsx', 'png').

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих извлеченные данные.
        """
        return await self.data_processor.process_file(file_data, file_type)