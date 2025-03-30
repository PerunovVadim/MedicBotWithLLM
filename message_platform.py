from abc import ABC, abstractmethod
from typing import Any, Optional

class MessagingPlatform(ABC):
    @abstractmethod
    async def send_message(
        self,
        chat_id: Any,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None,
    ) -> None:
        pass

    @abstractmethod
    def setup_handlers(self, message_handler, command_handlers: dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def start_polling(self) -> None:
        pass