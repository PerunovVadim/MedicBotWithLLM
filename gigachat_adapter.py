from langchain_core.messages import AIMessage
from langchain_gigachat.chat_models import GigaChat
from base_llm_adapter import *

class GigaChatAdapter(BaseLLMAdapter):
    def __init__(self, system_prompt: str, credentials: str, **kwargs):
        self.model = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,
            **kwargs
        )
        self.system_prompt = system_prompt

    async def get_response(self, messages: List[BaseMessage]) -> str:
        response = await self.model.ainvoke(messages)
        return response.content

    def format_message(self, text: str, is_user: bool) -> BaseMessage:
        """
        Форматирует сообщение для GigaChat API.
        Важно: системное сообщение может быть только первым в диалоге.
        """
        if not is_user and text == self.system_prompt:
            # Только для системного промпта (первое сообщение)
            return SystemMessage(content=text)
        elif is_user:
            # Сообщения от пользователя
            return HumanMessage(content=text)
        else:
            # Ответы ассистента
            return AIMessage(content=text)