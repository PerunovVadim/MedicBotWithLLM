from abc import ABC, abstractmethod
from typing import List
from langchain_core.messages import BaseMessage

class BaseLLMAdapter(ABC):
    @abstractmethod
    def __init__(self, system_prompt: str, **kwargs):
        pass

    @abstractmethod
    async def get_response(self, messages: List[BaseMessage], context: dict = None,**kwargs) -> str:
        pass

    @abstractmethod
    def format_message(self, text: str, is_user: bool) -> BaseMessage:
        pass