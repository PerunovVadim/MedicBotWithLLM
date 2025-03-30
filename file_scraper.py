import io

from PIL import Image
from pytesseract import pytesseract

from base_scraper import *
import pandas as pd
import pdfplumber

class FileScraper(BaseScraper):
    """
    Класс FileScraper представляет собой адаптер для обработки файлов различных форматов.
    Наследуется от BaseScraper и реализует методы для извлечения данных из PDF, Excel и изображений.

    Методы:
        fetch_data: Асинхронный метод для обработки файлов в зависимости от их типа.
        _parse_pdf: Извлекает текст из PDF-файла.
        _parse_excel: Извлекает данные из Excel-файла.
        _parse_image: Извлекает текст из изображений с использованием OCR (Tesseract).
    """

    async def fetch_data(self, file_data: bytes, file_type: str) -> List[Dict[str, Any]]:
        """
        Асинхронно обрабатывает файлы различных типов и извлекает данные.

        Args:
            file_data (bytes): Двоичные данные файла.
            file_type (str): Тип файла (например, 'pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg').

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих извлеченные данные.
                                  В случае ошибки или неподдерживаемого формата возвращается пустой список.

        Описание логики:
        - Для PDF-файлов вызывается метод `_parse_pdf`.
        - Для Excel-файлов вызывается метод `_parse_excel`.
        - Для изображений вызывается метод `_parse_image`.
        - Если тип файла не поддерживается, возвращается пустой список.
        - При возникновении ошибки выводится сообщение об ошибке, и возвращается пустой список.
        """
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
        """
        Извлекает текст из PDF-файла.

        Args:
            file_data (bytes): Двоичные данные PDF-файла.

        Returns:
            List[Dict[str, str]]: Список словарей, где каждый словарь содержит текст одной страницы PDF.
                                  Ключ "content" содержит текст страницы.

        Описание логики:
        - Используется библиотека `pdfplumber` для открытия и чтения PDF-файла.
        - Для каждой страницы извлекается текст и сохраняется в виде словаря.
        """
        with pdfplumber.open(io.BytesIO(file_data)) as pdf:
            return [{"content": page.extract_text()} for page in pdf.pages]

    def _parse_excel(self, file_data):
        """
        Извлекает данные из Excel-файла.

        Args:
            file_data (bytes): Двоичные данные Excel-файла.

        Returns:
            List[Dict[str, Any]]: Список словарей, где каждый словарь представляет строку данных из Excel.
                                  Ключи словаря соответствуют заголовкам столбцов.

        Описание логики:
        - Используется библиотека `pandas` для чтения Excel-файла.
        - Данные преобразуются в список словарей с помощью метода `to_dict('records')`.
        """
        df = pd.read_excel(io.BytesIO(file_data))
        return df.to_dict('records')

    async def _parse_image(self, file_data):
        """
        Извлекает текст из изображения с использованием OCR (Tesseract).

        Args:
            file_data (bytes): Двоичные данные изображения.

        Returns:
            List[Dict[str, str]]: Список словарей, где каждый словарь содержит извлеченный текст.
                                  Ключ "text" содержит текст, распознанный на изображении.

        Описание логики:
        - Используется библиотека `PIL` для открытия изображения.
        - Библиотека `pytesseract` применяется для распознавания текста на изображении.
        - Результат сохраняется в виде словаря с ключом "text".
        """
        image = Image.open(io.BytesIO(file_data))
        text = pytesseract.image_to_string(image)
        return [{"text": text}]