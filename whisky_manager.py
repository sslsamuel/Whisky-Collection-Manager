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
            self.data = {[]}
        print(len(self.data))

    def save_data(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def search_bottles(self, query):
        return [b for b in self.data if query.lower() in b["name"].lower()]



# not implemented yet
class Bottle:
    def __init__(self, name, age, price, distillery):
        self.name = name
        self.age = age
        self.price = price
        self.distillery = distillery

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "distillery": self.distillery,
            "type": self.type,
            "age": self.age,
            "abv": self.abv,
            "price": self.price,
        }

# not implemented yet
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password  # Ideally hashed
        self.collection = []
        self.wishlist = []

    def add_to_collection(self, bottle):
        self.collection.append(bottle)

    def add_to_wishlist(self, bottle):
        self.wishlist.append(bottle)


