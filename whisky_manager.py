import json

class WhiskyManager:
 
    @classmethod
    def load_data(self):
        try:
            with open('whisky.json', 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
        return self.data
    
    # def save_data(self):
    #     with open('whisky.json', 'w') as file:
    #         json.dump(self.data, file, indent=4)

    @classmethod
    def search_bottles(cls, query, collection=None):
        if collection:
            return [bottle for bottle in collection if query.lower() in bottle["name"].lower()]
        data = cls.load_data()
        return [bottle for bottle in data if query.lower() in bottle["name"].lower()]


class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.collection = []
        self.add_user()

    def add_user(self):
        """Save a user to the database (users.json)"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
        except FileNotFoundError:
            users_data = []

        # Append new user data
        if not any(user['username'] == self.username for user in users_data): # Check if the user does not exist
            user = {"username": self.username, "password": self.password, "collection": self.collection}      
            users_data.append(user)
            User.save_to_json(users_data)

    @staticmethod
    def save_to_json(users_data):
            """Save the users data to the users.json file"""
            with open('users.json', 'w') as file:
                json.dump(users_data, file, indent=4)

    @classmethod
    def amend_collection(cls, user, bottle, add):
        """
        Amend a user's collection.
        """

        if add == True: # Add the bottle to the collection
            # Avoid adding duplicate bottles
            if bottle in user["collection"]:
                return None # exit the function

            # Add the bottle to the collection
            user["collection"].append(bottle)

        elif add == False: # Remove the bottle from the collection
            user["collection"] = [b for b in user["collection"] if b["id"] != bottle["id"]]

        users_data = cls.load_users()  # Load the users data
        for user_data in users_data:
            if user_data['username'] == user["username"]:
                user_data['collection'] = user["collection"]  # Update the user's collection
        cls.save_to_json(users_data)  # Save the updated data

        return None # exit the function

    @staticmethod
    def load_users():
        """Load all users from the users.json file"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
            return users_data
        except FileNotFoundError:
            return []

  
class Bottle(WhiskyManager):

    def __init__(self, bottle_id, name, distillery, age, abv, price, image_url):
        self.id = bottle_id
        self.name = name
        self.distillery = distillery
        self.age = age
        self.abv = abv
        self.price = price
        self.image_url = image_url

    @classmethod
    def get_bottle_by_id(cls, bottle_id):
        """
        Retrieve a bottle by its ID.
        """
        data = cls.load_data()
        return next((bottle for bottle in data if bottle['id'] == bottle_id), None)






