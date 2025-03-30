from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_gigachat.chat_models import GigaChat
from base_llm_adapter import *
from typing import List


class GigaChatAdapter(BaseLLMAdapter):
    """
    Класс GigaChatAdapter представляет собой адаптер для взаимодействия с моделью GigaChat.
    Наследуется от BaseLLMAdapter и реализует методы для обработки сообщений и получения ответов.

    Attributes:
        model: Экземпляр модели GigaChat, который используется для генерации ответов.
        system_prompt (str): Системное сообщение, которое задает контекст или инструкции для модели.
    """

    def __init__(self, system_prompt: str, credentials: str, **kwargs):
        """
        Инициализирует экземпляр класса GigaChatAdapter.

        Args:
            system_prompt (str): Системное сообщение, которое будет использоваться для настройки модели.
            credentials (str): Учетные данные для аутентификации в GigaChat.
            **kwargs: Дополнительные параметры для настройки модели GigaChat.
        """
        self.model = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,  # Отключение проверки SSL-сертификатов
            **kwargs
        )
        self.system_prompt = system_prompt

    async def get_response(self, messages: List[BaseMessage], context: dict = None, **kwargs) -> str:
        """
        Асинхронно получает ответ от модели GigaChat на основе переданных сообщений и контекста.

        Args:
            messages (List[BaseMessage]): Список сообщений, которые будут отправлены модели.
            context (dict, optional): Словарь с контекстными данными, которые будут добавлены к системному сообщению.
            **kwargs: Дополнительные параметры для вызова модели.

        Returns:
            str: Текст ответа, сгенерированный моделью.

        Описание логики:
        - Если контекст предоставлен, он добавляется к системному сообщению.
        - Если системное сообщение отсутствует, оно создается на основе контекста.
        - Модель вызывается с модифицированным списком сообщений, и возвращается текст ответа.
        """
        modified_messages = list(messages)

        if context:
            # Формируем строку с контекстными данными
            context_str = "Контекстные данные:\n" + "\n".join(
                [f"{k}: {v}" for k, v in context.items()]
            )

            # Находим существующее системное сообщение или создаем новое
            system_msg = next((msg for msg in modified_messages if isinstance(msg, SystemMessage)), None)
            if system_msg:
                system_msg.content += f"\n\n{context_str}"
            else:
                modified_messages.insert(0, SystemMessage(content=context_str))

        # Вызываем модель для генерации ответа
        response = await self.model.ainvoke(modified_messages, **kwargs)
        return response.content

    def format_message(self, text: str, is_user: bool) -> BaseMessage:
        """
        Форматирует текстовое сообщение в соответствующий тип сообщения (SystemMessage, HumanMessage или AIMessage).

        Args:
            text (str): Текст сообщения.
            is_user (bool): Флаг, указывающий, является ли сообщение пользовательским.

        Returns:
            BaseMessage: Объект сообщения одного из типов: SystemMessage, HumanMessage или AIMessage.

        Логика форматирования:
        - Если текст совпадает с системным промптом и не от пользователя, возвращается SystemMessage.
        - Если сообщение от пользователя, возвращается HumanMessage.
        - В противном случае возвращается AIMessage.
        """
        if not is_user and text == self.system_prompt:
            return SystemMessage(content=text)
        elif is_user:
            return HumanMessage(content=text)
        else:
            return AIMessage(content=text)