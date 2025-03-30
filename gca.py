from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_gigachat.chat_models import GigaChat
from ba import *


class GigaChatAdapter(BaseLLMAdapter):
    def __init__(self, system_prompt: str, credentials: str, **kwargs):
        self.model = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,
            **kwargs
        )
        self.system_prompt = system_prompt

    async def get_response(self, messages: List[BaseMessage], context: dict = None, **kwargs) -> str:
        modified_messages = list(messages)

        if context:
            context_str = "Контекстные данные:\n" + "\n".join(
                [f"{k}: {v}" for k, v in context.items()]
            )

            # Найти системное сообщение или создать новое
            system_msg = next((msg for msg in modified_messages if isinstance(msg, SystemMessage)), None)
            if system_msg:
                system_msg.content += f"\n\n{context_str}"
            else:
                modified_messages.insert(0, SystemMessage(content=context_str))

        response = await self.model.ainvoke(modified_messages, **kwargs)
        return response.content

    def format_message(self, text: str, is_user: bool) -> BaseMessage:
        if not is_user and text == self.system_prompt:
            return SystemMessage(content=text)
        elif is_user:
            return HumanMessage(content=text)
        else:
            return AIMessage(content=text)