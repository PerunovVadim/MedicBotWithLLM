from abc import ABC, abstractmethod


class DatabaseHandler(ABC):
    @abstractmethod
    def connect(self):
        """Подключение к базе данных"""
        pass

    @abstractmethod
    def close(self):
        """Закрытие соединения с базой данных"""
        pass

    @abstractmethod
    def is_user_verified(self, user_id):
        """Проверка верификации пользователя"""
        pass

    @abstractmethod
    def is_user_registered(self, user_id):
        """Проверка, зарегистрирован ли пользователь"""
        pass

    @abstractmethod
    def register_user(self, user_id, username, phone):
        """Регистрация нового пользователя"""
        pass

    @abstractmethod
    def create_call_request(self, user_id):
        """Создание запроса на обратный звонок"""
        pass

    @abstractmethod
    def get_pending_requests(self):
        """Получение ожидающих запросов"""
        pass

    @abstractmethod
    def update_call_status(self, request_id, status=True):
        """Обновление статуса звонка"""
        pass