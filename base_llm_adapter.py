from abc import ABC, abstractmethod
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

class BaseLLMAdapter(ABC):
    @abstractmethod
    def __init__(self, system_prompt: str, **kwargs):
        """Инициализация модели с системным промтом."""
        pass

    @abstractmethod
    async def get_response(self, messages: List[BaseMessage]) -> str:
        """Запрос к модели."""
        pass

    @abstractmethod
    def format_message(self, text: str, is_user: bool) -> BaseMessage:
        """Форматирование сообщения для модели."""
        pass