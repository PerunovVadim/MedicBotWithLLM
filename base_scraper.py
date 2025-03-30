from abc import ABC, abstractmethod
from typing import List, Optional,Dict,Any
from urllib.parse import quote
import re

class BaseScraper(ABC):
    @abstractmethod
    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        pass