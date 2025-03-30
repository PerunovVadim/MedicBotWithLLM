import json

from ba import BaseLLMAdapter


class LLMService:
    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter
        self.reset_chat_history()  # Инициализируем историю с системным сообщением

    def reset_chat_history(self):
        self.chat_history = [self.adapter.format_message(self.adapter.system_prompt, is_user=False)]

    async def get_answer(self, user_input: str, context: dict = None,**kwargs) -> str:
        user_message = self.adapter.format_message(user_input, is_user=True)
        self.chat_history.append(user_message)

        response = await self.adapter.get_response(self.chat_history, context=context, **kwargs)
        self.chat_history.append(self.adapter.format_message(response, is_user=False))
        return response

