import json

class WhiskyManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.load_data()

    def load_data(self):
        try:
            with open(self.db_path, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
        print(len(self.data))

    def save_data(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def search_bottles(self, query):
        return [b for b in self.data if query.lower() in b["name"].lower()]

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user = {"username": self.username, "password": self.password}
        self.save_user()

    def save_user(self):
        """Save a user to the database (users.json)"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
        except FileNotFoundError:
            users_data = []

        # Append new user data
        user = {"username": self.username, "password": self.password}
        users_data.append(user)

        # Save back to JSON
        with open('users.json', 'w') as file:
            json.dump(users_data, file, indent=4)

    @staticmethod
    def load_users():
        """Load all users from the users.json file"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
            return users_data
        except FileNotFoundError:
            return []


