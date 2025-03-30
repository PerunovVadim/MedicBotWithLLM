from file_scraper import FileScraper
from website_scraper import WebsiteScraper

class DataProcessor:
    """
    Класс DataProcessor представляет собой процессор данных, который использует скраперы
    для получения информации с веб-сайтов и из файлов.

    Attributes:
        scrapers (Dict[str, BaseScraper]): Словарь, содержащий экземпляры скраперов
                                          для работы с веб-сайтами и файлами.
    """

    def __init__(self):
        """
        Инициализирует экземпляр класса. Создает словарь с экземплярами скраперов,
        которые будут использоваться для обработки данных.

        Описание логики:
        - Создаются экземпляры `WebsiteScraper` и `FileScraper`.
        - Эти экземпляры сохраняются в словаре `scrapers` для дальнейшего использования.
        """
        # Инициализируем скраперы без создания сессии
        self.scrapers = {
            "website": WebsiteScraper(),
            "file": FileScraper()
        }

    async def get_contacts(self):
        """
        Асинхронно получает контактную информацию с веб-сайта.

        Returns:
            str: Текстовое представление контактной информации.
                 Если данные не найдены, возвращается сообщение "Контакты не найдены".

        Описание логики:
        - Используется контекстный менеджер `async with` для управления жизненным циклом сессии.
        - Вызывается метод `fetch_data` у `WebsiteScraper` для получения данных.
        - Возвращается контактная информация из полученных данных.
        """
        # Используем async with для управления жизненным циклом сессии
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["contacts"] if data else "Контакты не найдены"

    async def get_schedule(self):
        """
        Асинхронно получает расписание с веб-сайта.

        Returns:
            str: Текстовое представление расписания.
                 Если данные не найдены, возвращается сообщение "Расписание не найдено".

        Описание логики:
        - Используется контекстный менеджер `async with` для управления жизненным циклом сессии.
        - Вызывается метод `fetch_data` у `WebsiteScraper` для получения данных.
        - Возвращается расписание из полученных данных.
        """
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["schedule"] if data else "Расписание не найдено"

    async def get_reminder(self):
        """
        Асинхронно получает напоминания для пациентов с веб-сайта.

        Returns:
            str: Текстовое представление напоминаний.
                 Если данные не найдены, возвращается сообщение "Памятка не найдена".

        Описание логики:
        - Используется контекстный менеджер `async with` для управления жизненным циклом сессии.
        - Вызывается метод `fetch_data` у `WebsiteScraper` для получения данных.
        - Возвращаются напоминания из полученных данных.
        """
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["patient_reminder"] if data else "Памятка не найдена"

    async def process_file(self, file_data, file_type):
        """
        Асинхронно обрабатывает файлы различных типов (PDF, Excel, изображения).

        Args:
            file_data: Двоичные данные файла.
            file_type (str): Тип файла (например, 'pdf', 'xlsx', 'png').

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих извлеченные данные.

        Описание логики:
        - Используется экземпляр `FileScraper` для обработки файлов.
        - Вызывается метод `fetch_data` у `FileScraper` для получения данных.
        - Если `FileScraper` требует контекстный менеджер (например, для aiohttp),
          необходимо добавить аналогичный блок `async with`.
        """
        # FileScraper может не требовать async with, если не использует aiohttp
        # Но если использует - нужно аналогично добавить контекстный менеджер
        scraper = self.scrapers["file"]
        return await scraper.fetch_data(file_data, file_type)