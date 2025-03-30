from file_scraper import FileScraper
from website_scraper import WebsiteScraper

class DataProcessor:
    def __init__(self):
        # Инициализируем скраперы без создания сессии
        self.scrapers = {
            "website": WebsiteScraper(),
            "file": FileScraper()
        }

    async def get_contacts(self):
        # Используем async with для управления жизненным циклом сессии
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["contacts"] if data else "Контакты не найдены"

    async def get_schedule(self):
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["schedule"] if data else "Расписание не найдено"

    async def get_reminder(self):
        async with self.scrapers["website"] as scraper:
            data = await scraper.fetch_data()
            return data[0]["patient_reminder"] if data else "Памятка не найдена"
    async def process_file(self, file_data, file_type):
        # FileScraper может не требовать async with, если не использует aiohttp
        # Но если использует - нужно аналогично добавить контекстный менеджер
        scraper = self.scrapers["file"]
        return await scraper.fetch_data(file_data, file_type)