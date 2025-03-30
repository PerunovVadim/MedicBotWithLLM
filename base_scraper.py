from abc import ABC, abstractmethod
from typing import List, Optional,Dict,Any
from urllib.parse import quote
import re
def make_phone_link(phone_text: str) -> str:
    cleaned_phone = re.sub(r'\D', '', phone_text)
    return f'<a href="tel:{cleaned_phone}">{phone_text}</a>'

def replace_address_with_link(text: str) -> str:
    address_pattern = re.compile(r"(ул\. Бабушкина, \d+)")
    def make_link(match):
        address = match.group(1)
        encoded_address = quote(address)
        return f'<a href="https://yandex.ru/maps/?text={encoded_address}">{address}</a>'
    return address_pattern.sub(make_link, text)
class BaseScraper(ABC):
    @abstractmethod
    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        pass