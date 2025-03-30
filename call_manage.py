from db_handler import *


class UserCallManager:
    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler

    def is_user_verified(self, user_id):
        return self.db_handler.is_user_verified(user_id)

    def is_user_registered(self, user_id):
        return self.db_handler.is_user_registered(user_id)

    def register_user(self, user_id, username, phone, full_name=""):
        return self.db_handler.register_user(user_id, username, phone, full_name)

    def create_call_request(self, user_id):
        return self.db_handler.create_call_request(user_id)

    def get_pending_requests(self):
        return self.db_handler.get_pending_requests()

    def update_call_status(self, request_id, status=True):
        return self.db_handler.update_call_status(request_id, status)

    def close(self):
        self.db_handler.close()