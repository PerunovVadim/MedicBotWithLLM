import io

from PIL import Image
from pytesseract import pytesseract

from base_scraper import *
import pandas as pd
import pdfplumber

class FileScraper(BaseScraper):
    async def fetch_data(self, file_data: bytes, file_type: str) -> List[Dict[str, Any]]:
        try:
            if file_type == 'pdf':
                return self._parse_pdf(file_data)
            elif file_type in ['xlsx', 'xls']:
                return self._parse_excel(file_data)
            elif file_type in ['png', 'jpg', 'jpeg']:
                return await self._parse_image(file_data)
            else:
                return []
        except Exception as e:
            print(f"Ошибка обработки файла: {e}")
            return []

    def _parse_pdf(self, file_data):
        with pdfplumber.open(io.BytesIO(file_data)) as pdf:
            return [{"content": page.extract_text()} for page in pdf.pages]

    def _parse_excel(self, file_data):
        df = pd.read_excel(io.BytesIO(file_data))
        return df.to_dict('records')

    async def _parse_image(self, file_data):
        image = Image.open(io.BytesIO(file_data))
        text = pytesseract.image_to_string(image)
        return [{"text": text}]