import json
import os
from base_scraper import *
from bs4 import BeautifulSoup
from config import *
import aiohttp

class WebsiteScraper(BaseScraper):
    """
    Класс WebsiteScraper представляет собой скрапер для парсинга данных с веб-сайтов.
    Наследуется от BaseScraper и реализует методы для извлечения информации о контактах,
    расписании и других данных с различных страниц сайта.

    Attributes:
        session: Асинхронная HTTP-сессия для выполнения запросов.
    """

    def __init__(self):
        """
        Инициализирует экземпляр класса. Создает атрибут session, который будет использоваться
        для выполнения HTTP-запросов.
        """
        self.session = None  # Не создаем сессию здесь

    async def __aenter__(self):
        """
        Метод контекстного менеджера для асинхронного входа. Создает новую HTTP-сессию.

        Returns:
            self: Возвращает текущий экземпляр класса.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Метод контекстного менеджера для асинхронного выхода. Закрывает HTTP-сессию.

        Args:
            exc_type: Тип исключения, если оно произошло.
            exc: Само исключение, если оно произошло.
            tb: Traceback исключения, если оно произошло.
        """
        await self.session.close()

    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Основной метод для получения данных с сайта. Выполняет парсинг различных разделов сайта
        и возвращает структурированные данные.

        Args:
            query (Optional[str]): Дополнительный параметр запроса (не используется).

        Returns:
            List[Dict[str, Any]]: Список словарей, содержащих извлеченные данные.
                                  В случае ошибки возвращается пустой список.

        Описание логики:
        - Парсит главную страницу сайта.
        - Парсит расписание отделения консультативной помощи.
        - Парсит напоминания для пациентов.
        - Возвращает объединенные данные.
        """
        async with aiohttp.ClientSession() as session:
            try:
                main_data = await self.parse_main_site(session)
                combined_contacts = main_data['contacts']
                combined_schedule = main_data['schedule']
                results_schedule = await self.parse_results_schedule(session)
                patient_reminder = await self.parse_patient_reminder(session)
                # Сохранение данных в JSON файлы (закомментировано)
                # self.save_to_json(self.clean_text(combined_contacts), "contacts.json")
                # self.save_to_json(self.clean_text(combined_schedule), "schedule.json")
                # self.save_to_json(self.clean_text(results_schedule), "results_schedule.json")
                # self.save_to_json(patient_reminder, "patient_reminder.json")
                return [{
                    "contacts": combined_contacts,
                    "schedule": combined_schedule,
                    "results": results_schedule,
                    "patient_reminder": patient_reminder
                }]
            except Exception as e:
                print(f"Ошибка парсинга сайта: {e}")
                return []

    async def parse_main_site(self, session):
        """
        Парсит главную страницу сайта для извлечения контактной информации и основного расписания.

        Args:
            session: Асинхронная HTTP-сессия.

        Returns:
            Dict[str, str]: Словарь, содержащий контакты и расписание.

        Описание логики:
        - Получает HTML-код главной страницы.
        - Использует BeautifulSoup для парсинга данных.
        - Возвращает контакты и объединенное расписание.
        """
        async with session.get(CONFIG["website_url"]) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            return {
                "contacts": self._parse_contacts(soup),
                "schedule": self._parse_main_schedule(soup) + "\n" + await self.parse_consultative_department_schedule(session)
            }

    async def parse_consultative_department_schedule(self, session):
        """
        Парсит страницу с расписанием отделения консультативной помощи.

        Args:
            session: Асинхронная HTTP-сессия.

        Returns:
            str: Текстовое представление расписания.

        Описание логики:
        - Получает HTML-код страницы с расписанием.
        - Использует BeautifulSoup для извлечения таблицы расписания.
        - Возвращает форматированный текст расписания.
        """
        async with session.get(CONFIG["consultative_url"]) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            return self._parse_consultative_schedule(soup)

    def _parse_consultative_schedule(self, soup):
        """
        Парсит таблицу расписания отделения консультативной помощи.

        Args:
            soup: Объект BeautifulSoup для парсинга HTML.

        Returns:
            str: Форматированный текст расписания.

        Описание логики:
        - Извлекает адрес отделения.
        - Находит таблицу расписания и парсит её строки.
        - Возвращает текстовое представление расписания.
        """
        result = []
        address_text = "ул. Бабушкина, 44 (вход с ул. Горького)"

        title = f"<b>Отделение консультативной помощи детям</b> {address_text}"
        result.append(f"\n{title}")
        schedule_table = soup.find('table', style=lambda s: 'width: 644px' in s if s else False)
        if schedule_table:
            rows = schedule_table.find_all('tr')[1:]  # Пропускаем заголовок
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    day = cols[0].get_text(strip=True)
                    time = cols[1].get_text(strip=True)
                    result.append(f"• {day}: {time}")
        else:
            result.append("Расписание не найдено")
        return '\n'.join(result)

    async def parse_patient_reminder(self, session):
        """
        Парсит страницу с напоминаниями для пациентов.

        Args:
            session: Асинхронная HTTP-сессия.

        Returns:
            Dict[str, List[str]]: Словарь, где ключи — это заголовки, а значения — списки напоминаний.

        Описание логики:
        - Находит все заголовки напоминаний.
        - Извлекает связанные с ними пункты списка.
        - Возвращает словарь напоминаний.
        """
        async with session.get(CONFIG["lab_url"]) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            reminders = {}
            strong_headers = soup.find_all("strong", style=re.compile(r"color:\s*#21347d;"))
            for strong in strong_headers:
                title = strong.get_text(strip=True).replace("\xa0", " ")
                if not title:
                    continue
                next_ol = strong.find_next("ol")
                if next_ol:
                    items = [li.get_text(strip=True) for li in next_ol.find_all("li")]
                    reminders[title] = items
            return reminders if reminders else "Нужные памятки не найдены"

    def _parse_results_schedule(self, soup):
        """
        Парсит расписание выдачи результатов анализов.

        Args:
            soup: Объект BeautifulSoup для парсинга HTML.

        Returns:
            str: Форматированный текст расписания.

        Описание логики:
        - Находит все элементы с расписанием.
        - Извлекает время для каждого дня недели.
        - Возвращает текстовое представление расписания.
        """
        result = []
        schedule_entries = soup.find_all('p', style=lambda s: 'font-family' in s if s else False)
        days = {
            "понедельник - пятница": None,
            "суббота": None,
            "воскресенье": None
        }
        for entry in schedule_entries:
            text = entry.get_text(strip=True)
            if "понедельник - пятница" in text:
                days["понедельник - пятница"] = self.extract_time(text)
            elif "суббота" in text:
                days["суббота"] = self.extract_time(text)
            elif "воскресенье" in text:
                days["воскресенье"] = self.extract_time(text)
        if days["понедельник - пятница"]:
            result.append(f" Понедельник - Пятница: {days['понедельник - пятница']}")
        if days["суббота"]:
            result.append(f" Суббота: {days['суббота']}")
        if days["воскресенье"]:
            result.append(f" Воскресенье: {days['воскресенье']}")
        return '\n'.join(result) if result else "Расписание выдачи результатов не найдено"

    def extract_time(self, text):
        """
        Извлекает временной интервал из текста.

        Args:
            text (str): Текст, содержащий временной интервал.

        Returns:
            str: Временной интервал в формате "HH:MM - HH:MM" или "Не указано".
        """
        time_match = re.search(r"\d{2}:\d{2} - \d{2}:\d{2}", text)
        return time_match.group(0) if time_match else "Не указано"

    def clean_text(self, text):
        """
        Очищает текст от HTML-тегов и лишних пустых строк.

        Args:
            text (str): Исходный текст.

        Returns:
            str: Очищенный текст.
        """
        text = re.sub(r'<.*?>', '', text)  # Убираем HTML
        text = re.sub(r'\n+', '\n', text).strip()  # Убираем лишние пустые строки
        return text

    def save_to_json(self, data, filename):
        """
        Сохраняет данные в JSON-файл.

        Args:
            data: Данные для сохранения.
            filename (str): Имя файла.

        Описание логики:
        - Создает директорию, если она не существует.
        - Сохраняет данные в указанный файл в формате JSON.
        """
        try:
            folder = 'data'
            if not os.path.exists(folder):
                os.makedirs(folder)
            file_path = os.path.join(folder, filename)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f" Данные успешно сохранены в {file_path}")
        except Exception as e:
            print(f"Ошибка сохранения в {filename}: {e}")

    def _parse_contacts(self, soup):
        """
        Парсит контактную информацию с главной страницы.

        Args:
            soup: Объект BeautifulSoup для парсинга HTML.

        Returns:
            str: Форматированный текст с контактами.

        Описание логики:
        - Извлекает телефонные номера и адреса.
        - Форматирует их в удобочитаемый вид.
        """
        phones = []
        main_phone_text = "Телефон единого центра обработки звонков диагностической поликлиники"
        main_phone = soup.find(
            lambda tag: tag.name == 'p' and main_phone_text in tag.get_text(strip=True).replace('\xa0', ' '))
        if main_phone:
            phone_number = main_phone.find('strong', style=lambda s: s and 'color' in s.lower())
            if phone_number:
                phone_text = phone_number.get_text(strip=True)
                phones.append(f" <b>Единый центр:</b> {phone_text}")
        student_block = soup.find(
            lambda tag: tag.name == 'p' and 'СТУДЕНТАМ ЧГМА' in tag.get_text(strip=True).replace('\xa0', ' '))
        if student_block:
            student_phones = student_block.find_all('strong', style=lambda s: s and 'color' in s.lower())
            if student_phones:
                phones.append("\n <b>Для студентов ЧГМА:</b>")
                for phone in student_phones:
                    phone_text = phone.get_text(strip=True)
                    phones.append(f" {phone_text}")
                address_text = "ул. Бабушкина, 48 (к терапевту Котовщиковой И.А.)"

                phones.append(f"\n Адрес: {address_text}")
        return '\n'.join(phones) if phones else "Телефоны не найдены"

    def _parse_main_schedule(self, soup):
        """
        Парсит основное расписание с главной страницы.

        Args:
            soup: Объект BeautifulSoup для парсинга HTML.

        Returns:
            str: Форматированный текст с расписанием.

        Описание логики:
        - Извлекает таблицы расписания.
        - Парсит каждую таблицу и форматирует данные.
        """
        tables = soup.find_all('table', style=lambda s: 'width: 350px' in s if s else False)
        result = []
        sections = [
            ("Диагностическая поликлиника (ул. Бабушкина, 44)", tables[0] if len(tables) > 0 else None),
            ("Сдача анализов (Диагностическая поликлиника, ул. Бабушкина, 44)", tables[1] if len(tables) > 1 else None),
            ("Сдача анализов (Бактериологическая лаборатория, ул. Бабушкина, 46)",
             tables[2] if len(tables) > 2 else None)
        ]
        for title, table in sections:
            if table:

                result.append(f"\n<b>{title}</b>")
                parsed_table = self._parse_table(table)
                result.extend(parsed_table)
        return '\n'.join(result) if result else "Расписание не найдено"

    def _parse_table(self, table):
        """
        Парсит таблицу расписания.

        Args:
            table: HTML-таблица.

        Returns:
            List[str]: Список строк с расписанием.

        Описание логики:
        - Извлекает строки таблицы.
        - Форматирует данные для каждого дня недели.
        """
        result = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 2:
                day = cols[0].get_text(strip=True)
                time = cols[1].get_text(' ', strip=True)
                result.append(f"• {day}: {time}")
        return result