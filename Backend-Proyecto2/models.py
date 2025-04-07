fake_users_db = {}

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password