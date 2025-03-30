from datetime import datetime

import psycopg2

from db_handler import *

class PostgreSQLHandler(DatabaseHandler):
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None
        self.connect()

    def get_pending_requests_by_user(self, user_id):
        try:
            self.cursor.execute("""
                SELECT * FROM call_requests
                WHERE user_id = %s AND call_status = FALSE
                ORDER BY request_time DESC
            """, (user_id,))
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error fetching pending requests: {e}")
            return []

    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_user_by_id(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None

    def is_user_verified(self, user_id):
        """Проверка верификации пользователя"""
        try:
            self.cursor.execute("SELECT is_verified FROM users WHERE user_id = %s", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else False
        except Exception as e:
            print(f"Error checking user verification: {e}")
            return False

    def is_user_registered(self, user_id):
        """Проверка, зарегистрирован ли пользователь"""
        try:
            self.cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error checking user registration: {e}")
            return False

    def register_user(self, user_id, username, phone, full_name=""):
        try:
            if self.is_user_registered(user_id):
                return True

            self.cursor.execute("""
                INSERT INTO users (user_id, username, phone, full_name, is_verified, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, username, phone, full_name, False, datetime.now()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            self.conn.rollback()
            return False

    def create_call_request(self, user_id):
        try:
            self.cursor.execute("SELECT phone FROM users WHERE user_id = %s", (user_id,))
            user = self.cursor.fetchone()
            if not user:
                return False

            phone = user[0]
            self.cursor.execute("""
                INSERT INTO call_requests (user_id, phone, request_time, call_status)
                VALUES (%s, %s, %s, %s)
            """, (user_id, phone, datetime.now(), False))  # Используем False для "pending"
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Call request error: {e}")
            self.conn.rollback()
            return False

    def get_pending_requests(self):
        """Получение ожидающих запросов"""
        try:
            self.cursor.execute("SELECT * FROM call_requests WHERE call_status = 'pending'")
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error fetching pending requests: {e}")
            return []

    def update_call_status(self, request_id, status=True):
        try:
            self.cursor.execute("""
                UPDATE call_requests SET call_status = %s WHERE request_id = %s
            """, (status, request_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating call status: {e}")
            self.conn.rollback()
            return False